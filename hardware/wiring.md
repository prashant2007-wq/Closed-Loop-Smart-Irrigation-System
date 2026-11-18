# Wiring (ESP32 DevKit V1)

| From | To | Note |
|---|---|---|
| Soil sensor VCC | ESP32 3V3 | capacitive sensor, 3.3 V |
| Soil sensor GND | ESP32 GND | |
| Soil sensor AO  | GPIO34 | ADC1 channel (works with Wi-Fi on) |
| Rain sensor AO (optional) | GPIO35 | set `USE_RAIN_SENSOR 1` |
| MOSFET module SIG/IN | GPIO26 | control signal |
| MOSFET module GND | ESP32 GND **and** supply GND | common ground is required |
| MOSFET module VIN+ | external 5 V supply + | pump power only |
| MOSFET module V-/OUT- | pump negative | low-side switching |
| Pump positive | external 5 V supply + | |
| 1N4007 | across pump | cathode (stripe) to pump +, anode to pump - |
| ESP32 | USB from Mac | logic power |

**Important:** the IRF520 is not a true logic-level MOSFET; at 3.3 V gate drive it may not switch fully on and can run hot.
Test it first. Better options: a logic-level MOSFET (e.g. IRLZ44N / IRLB8721) or a 5 V relay module with a transistor driver
(set `PUMP_ACTIVE_HIGH 0` if the relay board is active-low).
Keep pump wiring off the breadboard and keep all electronics away from water.
