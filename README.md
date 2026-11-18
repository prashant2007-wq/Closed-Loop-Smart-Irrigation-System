# Closed-Loop Smart Irrigation System (ESP32)

Embedded Systems Lab project - Newton School of Technology '25 (RU)
Author: Prashant S. Bisht (Enrollment No. 2501010346)

An IoT-based automatic watering system. A capacitive soil moisture sensor feeds an ESP32, which switches a 5 V
pump through a MOSFET driver. Watering starts below 35 % moisture and stops at 60 %, with safety limits
(max pump run time, soak delay, sensor-fault detection). Optional Wi-Fi/MQTT telemetry and remote commands.

## Repository contents
```
firmware/smart_irrigation/   complete source code (Arduino framework)
  smart_irrigation.ino         main program (state machine + MQTT)
  config.h                     pins, calibration, thresholds, safety timing
  secrets.h.example            template for Wi-Fi / MQTT credentials
hardware/wiring.md, bom.md   wiring table and bill of materials
docs/Final_Project_Report.pdf  final project report (PDF)
docs/images/                 diagrams used in the report
tools/build_report.py        regenerates the PDF report
platformio.ini               PlatformIO build config
```

## Build and flash
**Arduino IDE:** install the *esp32* board package, library *PubSubClient*, open `smart_irrigation.ino`,
copy `secrets.h.example` to `secrets.h`, select board *ESP32 Dev Module*, upload.

**PlatformIO (VS Code, macOS):** `pio run -t upload && pio device monitor`

No network? Set `ENABLE_MQTT 0` in `config.h` - the controller works fully offline.

## Calibrate before use
1. Open Serial Monitor (115200). Note the `raw` value with the sensor in dry air -> `SOIL_DRY_ADC`.
2. Put the sensing part in water -> `SOIL_WET_ADC`.
3. Adjust `MOISTURE_ON_PCT` / `MOISTURE_OFF_PCT` for your plant.

## MQTT
Telemetry on `irrigation/telemetry` (JSON). Commands on `irrigation/cmd`: `WATER`, `STOP`, `RESET`.

## Hardware warnings
- IRF520 is not logic-level at 3.3 V; verify it switches fully or use a logic-level MOSFET / relay.
- Share GND between ESP32 and pump supply; keep pump current off the breadboard; add the flyback diode.
- Keep electronics dry.

## Status
Firmware written to the design in the report. Default thresholds/calibration values are starting points; test
results must be recorded on your own hardware (see report Section 9).
