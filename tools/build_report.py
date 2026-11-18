"""Builds docs/Final_Project_Report.pdf  (pip install reportlab matplotlib)"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table,
                                TableStyle, Image, Preformatted, KeepTogether)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "docs", "images")
OUT = os.path.join(ROOT, "docs", "Final_Project_Report.pdf")
os.makedirs(IMG, exist_ok=True)

def box(ax, x, y, w, h, text, fc="#E8F0FE"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02", fc=fc, ec="#1a3d7c", lw=1.4))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center", fontsize=9)

def arrow(ax, p1, p2, label=None):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=14, lw=1.4, color="#333"))
    if label:
        ax.text((p1[0]+p2[0])/2, (p1[1]+p2[1])/2 + 0.12, label, ha="center", fontsize=7.5, color="#444")

# ---- Diagram 1: block diagram / closed loop ----
fig, ax = plt.subplots(figsize=(9, 3.6)); ax.set_xlim(0, 10); ax.set_ylim(0, 4); ax.axis("off")
box(ax, 0.2, 1.6, 1.7, 0.9, "Soil moisture\nsensor (GPIO34)", "#DFF5E1")
box(ax, 2.6, 1.6, 1.7, 0.9, "ESP32\ncontroller", "#FFF3CD")
box(ax, 5.0, 1.6, 1.7, 0.9, "MOSFET driver\n(GPIO26)", "#E8F0FE")
box(ax, 7.4, 1.6, 1.7, 0.9, "5 V water pump\n+ 1N4007", "#E8F0FE")
arrow(ax, (1.9, 2.05), (2.6, 2.05), "raw ADC")
arrow(ax, (4.3, 2.05), (5.0, 2.05), "ON/OFF")
arrow(ax, (6.7, 2.05), (7.4, 2.05), "pump current")
box(ax, 3.7, 0.1, 2.6, 0.7, "Plant soil (moisture changes)", "#F5E6D3")
arrow(ax, (8.2, 1.6), (6.3, 0.5)); arrow(ax, (3.7, 0.5), (1.0, 1.6), "feedback")
box(ax, 5.0, 3.1, 3.2, 0.7, "Wi-Fi / MQTT dashboard (optional)", "#EEE")
arrow(ax, (3.9, 2.5), (5.0, 3.35)); 
ax.text(5, 3.95, "Closed-loop control", ha="center", fontsize=11, weight="bold")
fig.savefig(os.path.join(IMG, "block_diagram.png"), dpi=170, bbox_inches="tight"); plt.close(fig)

# ---- Diagram 2: state machine ----
fig, ax = plt.subplots(figsize=(9, 3.8)); ax.set_xlim(0, 10); ax.set_ylim(0, 4.2); ax.axis("off")
box(ax, 0.3, 1.6, 1.8, 0.9, "IDLE", "#DFF5E1")
box(ax, 3.6, 1.6, 1.8, 0.9, "WATERING\n(pump ON)", "#FFF3CD")
box(ax, 7.0, 1.6, 1.8, 0.9, "SOAKING\n(pump OFF, wait)", "#E8F0FE")
box(ax, 3.6, 3.2, 1.8, 0.7, "FAULT (pump OFF)", "#F8D7DA")
arrow(ax, (2.1, 2.05), (3.6, 2.05), "moisture < 35 %")
arrow(ax, (5.4, 2.05), (7.0, 2.05), "moisture >= 60 %\nor 20 s timeout")
arrow(ax, (7.9, 1.6), (1.2, 1.6)); ax.text(4.5, 1.15, "soak time (60 s) elapsed", fontsize=7.5, ha="center", color="#444")
arrow(ax, (4.5, 2.5), (4.5, 3.2)); ax.text(5.5, 2.8, "sensor out of range /\n3 timeouts in a row", fontsize=7.5)
fig.savefig(os.path.join(IMG, "state_machine.png"), dpi=170, bbox_inches="tight"); plt.close(fig)

# ---- Report ----
ss = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontSize=15, textColor=colors.HexColor("#1a3d7c"), spaceBefore=14, spaceAfter=6)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontSize=12, spaceBefore=8, spaceAfter=4)
B = ParagraphStyle("B", parent=ss["BodyText"], fontSize=10.3, leading=14.5, alignment=4)
C = ParagraphStyle("C", parent=B, alignment=1)
CODE = ParagraphStyle("CODE", fontName="Courier", fontSize=6.8, leading=8.2)
def P(t): return Paragraph(t, B)
def bullets(items): return [Paragraph("&bull; " + i, B) for i in items]
def table(data, widths, hdr=True):
    data = [[Paragraph(str(c), ParagraphStyle("t", parent=B, fontSize=9, leading=11.5, alignment=0)) for c in r] for r in data]
    t = Table(data, colWidths=widths, repeatRows=1)
    st = [("GRID", (0,0), (-1,-1), 0.5, colors.grey), ("VALIGN", (0,0), (-1,-1), "TOP")]
    if hdr: st.append(("BACKGROUND", (0,0), (-1,0), colors.HexColor("#DCE6F7")))
    t.setStyle(TableStyle(st)); return t

def footer(c, d):
    c.saveState(); c.setFont("Helvetica", 8); c.setFillColor(colors.grey)
    c.drawString(2*cm, 1.2*cm, "Closed-Loop Smart Irrigation System - Embedded Systems Lab")
    c.drawRightString(A4[0]-2*cm, 1.2*cm, f"Page {d.page}"); c.restoreState()

doc = SimpleDocTemplate(OUT, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm,
                        title="Closed-Loop Smart Irrigation System - Final Project Report", author="Prashant S. Bisht")
S = []
# Title page
S += [Spacer(1, 3*cm), Paragraph("<b>Closed-Loop Smart Irrigation System</b>", ParagraphStyle("T", parent=C, fontSize=26, leading=32, textColor=colors.HexColor("#1a3d7c"))),
      Spacer(1, 6), Paragraph("An IoT-based automatic watering system using ESP32", ParagraphStyle("st", parent=C, fontSize=13)),
      Spacer(1, 1.2*cm), Paragraph("<b>Final Project Report</b><br/>Embedded Systems Lab", ParagraphStyle("t2", parent=C, fontSize=14, leading=20)),
      Spacer(1, 1.5*cm),
      table([["Submitted by", "Prashant S. Bisht"], ["Enrollment No.", "2501010346"],
             ["Programme", "B.Tech Computer Science and Engineering"], ["Batch", "Newton School of Technology '25 (RU)"],
             ["Course", "Embedded Systems Lab"], ["Source code", "firmware/smart_irrigation/ in the project repository"]],
            [4.5*cm, 11*cm], hdr=False), PageBreak()]

S += [Paragraph("Abstract", H1), P(
 "This report describes the design and implementation of a closed-loop smart irrigation system. A capacitive soil moisture "
 "sensor measures the actual water content of the soil; an ESP32 microcontroller compares the reading with a lower and an upper "
 "threshold (hysteresis) and switches a 5 V DC pump through a MOSFET driver. Because the sensor continuously measures the result of "
 "every watering action, the system is a feedback (closed-loop) controller rather than a timer. Safety features include a maximum "
 "pump run time, a soak delay, sensor-fault detection and a latched fault state. The ESP32's Wi-Fi allows optional MQTT telemetry and "
 "remote commands without making the control loop depend on the network.")]

S += [Paragraph("1. Introduction", H1), P(
 "Manual or timer-based watering ignores the real condition of the soil and leads to over- or under-watering and wasted water. "
 "This project automates irrigation using sensor feedback so that the plant receives water only when needed and only until a target "
 "moisture level is reached."),
 Paragraph("1.1 Objectives", H2)] + bullets([
 "Measure soil moisture continuously and convert it to a percentage.",
 "Switch a water pump automatically using threshold control with hysteresis.",
 "Protect the hardware and plant using timeouts, soak delay and fault detection.",
 "Provide optional IoT monitoring and control over Wi-Fi/MQTT."])

S += [Paragraph("2. Components", H1), table([
 ["Component", "Function"],
 ["ESP32 DevKit V1 (30-pin)", "Main controller: reads the ADC, runs the control logic, drives the pump switch, provides Wi-Fi."],
 ["Capacitive soil moisture sensor", "Outputs an analog voltage that falls as soil moisture rises. Capacitive types resist corrosion."],
 ["IRF520 MOSFET module", "Electronic switch so a 3.3 V GPIO can control the pump current. Not a true logic-level device (see Section 8)."],
 ["1N4007 diode", "Flyback diode across the pump (cathode to +, anode to -) to absorb the inductive voltage spike."],
 ["5 V mini DC submersible pump", "Delivers water from the reservoir to the plant through a tube."],
 ["5 V 2 A external supply", "Powers the pump separately from the controller."],
 ["Breadboard and jumper wires", "Prototype connections (pump current wiring kept off the breadboard)."],
 ["Raspberry Pi Pico 2 W (optional)", "Available for extension experiments; not required for the base design."]],
 [5.2*cm, 11.8*cm])]

S += [Paragraph("3. System Architecture", H1), Image(os.path.join(IMG, "block_diagram.png"), width=16.5*cm, height=6.6*cm),
 P("<i>Figure 1: Block diagram and feedback path.</i>"),
 P("The sensor output is read on GPIO34 (ADC1). The ESP32 decides, then drives GPIO26 connected to the MOSFET module. The pump is powered by an "
   "external supply sharing a common ground with the ESP32. Water entering the soil changes the sensor reading, closing the loop.")]

S += [Paragraph("4. Circuit Connections", H1), table([
 ["From", "To", "Note"],
 ["Soil sensor VCC / GND", "ESP32 3V3 / GND", "3.3 V supply"],
 ["Soil sensor AO", "GPIO34", "ADC1 input"],
 ["MOSFET module SIG", "GPIO26", "control signal"],
 ["MOSFET GND", "ESP32 GND and supply GND", "common ground"],
 ["Supply +5 V", "MOSFET VIN+ and pump +", "pump power"],
 ["MOSFET V-", "Pump -", "low-side switching"],
 ["1N4007", "Across pump", "cathode to pump +"]], [5*cm, 6.5*cm, 5.5*cm])]

S += [Paragraph("5. Working Principle", H1), P(
 "Every 500 ms the firmware averages 16 ADC samples, converts the result to percent using the dry and wet calibration points, "
 "and runs the state machine of Figure 2. When moisture falls below 35 % the pump starts. It stops when moisture reaches 60 % or after "
 "20 seconds (whichever comes first). A 60-second soak period follows so water can spread to the sensor before the next decision; "
 "without it the controller would over-react to a reading that has not yet caught up."),
 Image(os.path.join(IMG, "state_machine.png"), width=16.5*cm, height=7*cm), P("<i>Figure 2: Controller state machine.</i>"),
 Paragraph("5.1 Open-loop versus closed-loop", H2),
 P("An open-loop system runs the pump for a fixed time regardless of the soil. This system uses measured moisture as feedback, so the "
   "amount of water adapts to the soil, plant and weather conditions.")]

S += [Paragraph("6. Software Design", H1), P(
 "The firmware (Arduino framework for ESP32) is non-blocking: timing uses millis() and the network code never stalls the loop."),
 table([["Feature", "Implementation"],
  ["Sensing", "16-sample average on a 12-bit ADC with 11 dB attenuation"],
  ["Conversion", "percent = (DRY - raw) x 100 / (DRY - WET), constrained to 0-100"],
  ["Control", "Hysteresis: ON below 35 %, OFF at or above 60 %"],
  ["Safety", "20 s max run, 60 s soak, 3 consecutive timeouts latch FAULT; out-of-range ADC value latches FAULT"],
  ["Fail-safe", "Pump driven OFF before the pin is configured as output at boot; pump forced OFF in FAULT"],
  ["Optional rain input", "Skips irrigation when the rain sensor reads wet"],
  ["IoT", "JSON telemetry every 5 s to irrigation/telemetry; commands WATER, STOP, RESET on irrigation/cmd"],
  ["Logging", "CSV lines on the serial port: time, raw, moisture, rain, state, pump"]], [4*cm, 13*cm])]

S += [Paragraph("7. Calibration", H1)] + bullets([
 "Read the raw value with the sensor in dry air and record it as SOIL_DRY_ADC.",
 "Read the raw value with the sensing part in water and record it as SOIL_WET_ADC.",
 "Choose MOISTURE_ON_PCT and MOISTURE_OFF_PCT to suit the plant; keep a wide gap to avoid short cycling.",
 "The default values in config.h (3200 and 1400) are starting points only; each sensor differs."])

S += [Paragraph("8. Hardware Considerations and Safety", H1)] + bullets([
 "<b>IRF520:</b> its gate threshold is designed for about 10 V drive, so at 3.3 V it may switch only partially, giving a high on-resistance and heat. "
 "Verify with a multimeter (voltage across the pump) or substitute a logic-level MOSFET such as IRLZ44N or a relay module.",
 "<b>Power:</b> check the pump's rated voltage and stall current; use a supply with margin.",
 "<b>Flyback diode:</b> required across the pump because the motor is an inductive load.",
 "<b>Common ground:</b> the ESP32 and pump supply must share ground.",
 "<b>Water safety:</b> keep electronics and connections dry and insulated.",
 "<b>Dry-run protection:</b> the max run time and fault latch stop the pump if the tank is empty."])

S += [Paragraph("9. Testing Plan and Results", H1), P(
 "The table lists the tests to be run on the assembled prototype. The Observed column is left for the measured result so that the report "
 "reflects actual bench data."),
 table([["No.", "Test", "Expected", "Observed"],
  ["1", "Sensor in dry air - raw and %", "Raw near SOIL_DRY_ADC, about 0 %", ""],
  ["2", "Sensor in water - raw and %", "Raw near SOIL_WET_ADC, about 100 %", ""],
  ["3", "Dry soil", "Pump starts below 35 %", ""],
  ["4", "Watering in progress", "Pump stops at 60 %", ""],
  ["5", "Soak period", "No restart for 60 s after a burst", ""],
  ["6", "Empty tank", "Three 20 s bursts then FAULT, pump OFF", ""],
  ["7", "Sensor unplugged", "FAULT, pump OFF", ""],
  ["8", "MQTT WATER / STOP / RESET", "Commands accepted in valid states", ""],
  ["9", "Wi-Fi unplugged", "Local control continues", ""]],
  [1.2*cm, 5.5*cm, 7*cm, 3.3*cm])]

S += [Paragraph("10. Limitations and Future Scope", H1)] + bullets([
 "A single sensor represents only one point in the soil.",
 "Fixed thresholds; per-plant profiles could be stored on the device.",
 "Water-level sensing in the reservoir would warn before the tank runs empty.",
 "A web or mobile dashboard, notifications, and Pico 2 W nodes for multiple zones.",
 "Battery or solar power for field deployment; replace the prototype pump driver with a logic-level MOSFET on a soldered board."])

S += [Paragraph("11. Conclusion", H1), P(
 "The project applies sensors, an actuator, feedback control and IoT connectivity to a practical problem. The design uses hysteresis, "
 "soak delay and fault handling to keep the control robust, and keeps the controller independent of the network. Calibration and the "
 "hardware checks described above are needed on the physical prototype before the results in Section 9 are recorded.")]

S += [Paragraph("12. Repository Layout", H1), Preformatted(
"firmware/smart_irrigation/  smart_irrigation.ino, config.h, secrets.h.example\n"
"hardware/                   wiring.md, bom.md\n"
"docs/                       Final_Project_Report.pdf, images/\n"
"tools/build_report.py       regenerates this report\n"
"platformio.ini, README.md, LICENSE", CODE)]

# Appendix: source code
S += [PageBreak(), Paragraph("Appendix A: config.h", H1)]
for fn, title in [("config.h", None), ("smart_irrigation.ino", "Appendix B: smart_irrigation.ino")]:
    if title: S += [PageBreak(), Paragraph(title, H1)]
    with open(os.path.join(ROOT, "firmware", "smart_irrigation", fn), encoding="utf-8") as f:
        S.append(Preformatted(f.read(), CODE))

doc.build(S, onFirstPage=lambda c, d: None, onLaterPages=footer)
print("Wrote", OUT)
