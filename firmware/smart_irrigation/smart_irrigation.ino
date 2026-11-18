/*
 * Closed-Loop Smart Irrigation System
 * Embedded Systems Lab - Newton School of Technology '25 (RU)
 * Author: Prashant S. Bisht
 *
 * Control idea (closed loop):
 *   Soil moisture sensor -> ESP32 compares with thresholds -> MOSFET -> pump -> soil
 *   -> sensor measures the new moisture -> repeat.
 * Hysteresis (ON at 35 %, OFF at 60 %) prevents rapid pump chatter.
 * The control loop never depends on Wi-Fi; MQTT is telemetry/commands only.
 */
#include <Arduino.h>
#include "config.h"

#if ENABLE_MQTT
  #include <WiFi.h>
  #include <PubSubClient.h>
  #include "secrets.h"
  WiFiClient   wifiClient;
  PubSubClient mqtt(wifiClient);
#endif

enum State { ST_IDLE, ST_WATERING, ST_SOAKING, ST_FAULT };
static const char* STATE_NAME[] = { "IDLE", "WATERING", "SOAKING", "FAULT" };

State         state          = ST_IDLE;
unsigned long tLastSample    = 0;
unsigned long tPumpStart     = 0;
unsigned long tSoakStart     = 0;
unsigned long tLastPublish   = 0;
unsigned long tLastWifiTry   = 0;
unsigned long tLastMqttTry   = 0;
uint8_t       timeoutCount   = 0;
bool          pumpOn         = false;
int           rawSoil        = 0;
int           rawRain        = 4095;
float         moisturePct    = 0;
bool          raining        = false;
const char*   faultReason    = "";

// ---------- helpers ----------
int readAveraged(uint8_t pin, uint8_t n = 16) {
  long sum = 0;
  for (uint8_t i = 0; i < n; i++) { sum += analogRead(pin); delay(2); }
  return (int)(sum / n);
}

float rawToPercent(int raw) {
  float pct = (float)(SOIL_DRY_ADC - raw) * 100.0f / (float)(SOIL_DRY_ADC - SOIL_WET_ADC);
  return constrain(pct, 0.0f, 100.0f);
}

void pumpSet(bool on) {
  pumpOn = on;
  bool level = (on == (bool)PUMP_ACTIVE_HIGH);
  digitalWrite(PIN_PUMP, level ? HIGH : LOW);
}

void enterFault(const char* reason) {
  pumpSet(false);
  state = ST_FAULT;
  faultReason = reason;
  Serial.printf("!! FAULT: %s\n", reason);
}

void startWatering(const char* why) {
  pumpSet(true);
  tPumpStart = millis();
  state = ST_WATERING;
  Serial.printf(">> Pump ON (%s)\n", why);
}

void stopWatering(const char* why, bool timedOut) {
  pumpSet(false);
  tSoakStart = millis();
  state = ST_SOAKING;
  Serial.printf(">> Pump OFF (%s)\n", why);
  if (timedOut) {
    if (++timeoutCount >= MAX_CONSEC_TIMEOUTS)
      enterFault("pump ran max time repeatedly: empty tank, blocked pipe or sensor not responding");
  } else {
    timeoutCount = 0;
  }
}

// ---------- networking (non-blocking) ----------
#if ENABLE_MQTT
void onMqttMessage(char* topic, byte* payload, unsigned int len) {
  String cmd;
  for (unsigned int i = 0; i < len; i++) cmd += (char)payload[i];
  cmd.trim(); cmd.toUpperCase();
  if (cmd == "WATER" && state == ST_IDLE)              startWatering("remote command");
  else if (cmd == "STOP" && state == ST_WATERING)      stopWatering("remote stop", false);
  else if (cmd == "RESET" && state == ST_FAULT)        { timeoutCount = 0; state = ST_IDLE; Serial.println(">> Fault cleared"); }
}

void networkService() {
  unsigned long now = millis();
  if (WiFi.status() != WL_CONNECTED) {
    if (now - tLastWifiTry > 10000UL) { tLastWifiTry = now; WiFi.begin(WIFI_SSID, WIFI_PASSWORD); }
    return;
  }
  if (!mqtt.connected()) {
    if (now - tLastMqttTry > 5000UL) {
      tLastMqttTry = now;
      if (mqtt.connect(MQTT_CLIENT_ID)) mqtt.subscribe(MQTT_TOPIC_COMMAND);
    }
    return;
  }
  mqtt.loop();
  if (now - tLastPublish >= MQTT_PUBLISH_MS) {
    tLastPublish = now;
    char buf[200];
    snprintf(buf, sizeof(buf),
      "{\"raw\":%d,\"moisture\":%.1f,\"pump\":%s,\"state\":\"%s\",\"raining\":%s}",
      rawSoil, moisturePct, pumpOn ? "true" : "false", STATE_NAME[state], raining ? "true" : "false");
    mqtt.publish(MQTT_TOPIC_TELEMETRY, buf);
  }
}
#endif

// ---------- Arduino entry points ----------
void setup() {
  digitalWrite(PIN_PUMP, (PUMP_ACTIVE_HIGH ? LOW : HIGH));   // pump OFF before pin becomes output
  pinMode(PIN_PUMP, OUTPUT);
  pumpSet(false);
  pinMode(PIN_LED, OUTPUT);
  Serial.begin(115200);
  analogReadResolution(12);
  analogSetPinAttenuation(PIN_SOIL, ADC_11db);
  analogSetPinAttenuation(PIN_RAIN, ADC_11db);
  Serial.println("\nClosed-Loop Smart Irrigation System - boot");
  Serial.println("time_ms,raw,moisture_pct,rain,state,pump");

#if ENABLE_MQTT
  WiFi.mode(WIFI_STA);
  mqtt.setServer(MQTT_BROKER, MQTT_PORT);
  mqtt.setCallback(onMqttMessage);
#endif
}

void loop() {
  unsigned long now = millis();

  if (now - tLastSample >= SAMPLE_INTERVAL_MS) {
    tLastSample = now;

    // 1) SENSE
    rawSoil     = readAveraged(PIN_SOIL);
    moisturePct = rawToPercent(rawSoil);
#if USE_RAIN_SENSOR
    rawRain = readAveraged(PIN_RAIN);
    raining = (rawRain < RAIN_WET_ADC);
#endif

    // 2) CHECK SENSOR HEALTH
    if (state != ST_FAULT && (rawSoil < SOIL_RAW_MIN || rawSoil > SOIL_RAW_MAX))
      enterFault("soil sensor reading out of range (disconnected or shorted)");

    // 3) DECIDE + 4) ACT
    switch (state) {
      case ST_IDLE:
        if (moisturePct < MOISTURE_ON_PCT && !raining) startWatering("soil dry");
        break;
      case ST_WATERING:
        if (moisturePct >= MOISTURE_OFF_PCT)                 stopWatering("target moisture reached", false);
        else if (now - tPumpStart >= MAX_PUMP_RUN_MS)        stopWatering("max run time reached", true);
        break;
      case ST_SOAKING:
        if (now - tSoakStart >= SOAK_TIME_MS) state = ST_IDLE;
        break;
      case ST_FAULT:
        pumpSet(false);                                     // always keep pump off in FAULT
        break;
    }

    // LED: on while pumping, fast blink in FAULT
    if (state == ST_FAULT) digitalWrite(PIN_LED, (now / 250) % 2);
    else                   digitalWrite(PIN_LED, pumpOn ? HIGH : LOW);

    Serial.printf("%lu,%d,%.1f,%d,%s,%d\n", now, rawSoil, moisturePct, raining, STATE_NAME[state], pumpOn);
  }

#if ENABLE_MQTT
  networkService();
#endif
}
