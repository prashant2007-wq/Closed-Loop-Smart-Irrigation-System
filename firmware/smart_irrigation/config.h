// config.h - all tunable settings for the Closed-Loop Smart Irrigation System
// Board: ESP32 DevKit V1 (30-pin)
#pragma once

// ---------- Pins (ESP32 DevKit V1) ----------
#define PIN_SOIL   34   // Capacitive soil moisture sensor AO (ADC1, input-only)
#define PIN_RAIN   35   // Rain sensor AO (ADC1, input-only) - optional
#define PIN_PUMP   26   // Gate/IN signal to MOSFET module (or relay)
#define PIN_LED     2   // On-board LED: status indicator

// ---------- Pump driver ----------
// 1 = HIGH turns pump ON (MOSFET module).  0 = LOW turns pump ON (active-low relay).
#define PUMP_ACTIVE_HIGH 1

// ---------- Sensor calibration (RAW 12-bit ADC, 0-4095) ----------
// Capacitive sensor: HIGHER raw value = DRIER soil.
// Measure YOUR sensor: raw in dry air/dry soil -> SOIL_DRY_ADC, raw in a glass of water -> SOIL_WET_ADC.
#define SOIL_DRY_ADC  3200
#define SOIL_WET_ADC  1400

// Valid raw range; outside this the sensor is considered disconnected/faulty.
#define SOIL_RAW_MIN   300
#define SOIL_RAW_MAX  4000

// ---------- Control thresholds (percent moisture) ----------
#define MOISTURE_ON_PCT   35   // start watering below this
#define MOISTURE_OFF_PCT  60   // stop watering at/above this (hysteresis band 35-60)

// ---------- Safety timing ----------
#define SAMPLE_INTERVAL_MS   500UL     // sensor sampling period
#define MAX_PUMP_RUN_MS    20000UL     // hard cut-off for one watering burst
#define SOAK_TIME_MS       60000UL     // wait after a burst so water can reach the sensor
#define MAX_CONSEC_TIMEOUTS     3      // bursts that hit the time limit before FAULT latches

// ---------- Optional rain sensor ----------
#define USE_RAIN_SENSOR 0              // 1 = skip irrigation while raining
#define RAIN_WET_ADC  2000             // raw below this = raining (AO drops when wet)

// ---------- Optional IoT (Wi-Fi + MQTT) ----------
#define ENABLE_MQTT 1                  // 0 = fully offline controller
#define MQTT_PORT 1883
#define MQTT_TOPIC_TELEMETRY "irrigation/telemetry"
#define MQTT_TOPIC_COMMAND   "irrigation/cmd"   // payloads: WATER, STOP, RESET
#define MQTT_PUBLISH_MS 5000UL
