# 🚗 Raspberry Pi Pico Based J1939 CAN Simulation System

## 📌 Overview

This project simulates an automotive system using **Raspberry Pi Pico**, where analog inputs (via potentiometers) represent vehicle parameters. These values are processed, encoded following **J1939 CAN protocol principles**, and displayed on dual LCDs.

---

## 🎯 Features

* 🔹 Real-time sensor simulation using potentiometers
* 🔹 Conversion of analog signals to physical parameters
* 🔹 J1939-style data encoding (8-bit scaling)
* 🔹 Dual LCD output:

  * LCD1 → Raw vehicle data
  * LCD2 → CAN encoded data
* 🔹 Simple embedded implementation (no external libraries)

---

## 🧠 System Architecture

```
Potentiometers → ADC (Pico) → Mapping → Encoding → Display (LCD1 + LCD2)
```

---

## 🔧 Hardware Components

* Raspberry Pi Pico
* 3 × Potentiometers
* 2 × 16x2 LCD Displays
* Breadboard & Connecting Wires

---

## 🔌 Pin Configuration

### 📟 LCD1 (Raw Data)

| Signal | Pico Pin |
| ------ | -------- |
| RS     | GP0      |
| E      | GP1      |
| D4–D7  | GP2–GP5  |

### 📟 LCD2 (Encoded Data)

| Signal | Pico Pin |
| ------ | -------- |
| RS     | GP6      |
| E      | GP7      |
| D4–D7  | GP8–GP11 |

### 🎚️ Potentiometers

| Parameter | Pico Pin    |
| --------- | ----------- |
| Speed     | GP26 (ADC0) |
| Temp      | GP27 (ADC1) |
| Fuel      | GP28 (ADC2) |

---

## ⚙️ Working Principle

### 1️⃣ Analog Input Acquisition

* Potentiometers generate variable voltage
* Pico reads values via ADC (0–65535)

### 2️⃣ Parameter Mapping

Raw ADC values are converted into real-world units:

* Speed → 0–200 km/h
* Temperature → 20–120 °C
* Fuel → 0–100 %

---

### 3️⃣ J1939 Encoding

Each parameter is scaled to 8-bit format:

```
D0 = Speed × (255 / 200)
D1 = Temp  × (255 / 120)
D2 = Fuel  × (255 / 100)
```

---

### 4️⃣ CAN Frame Representation

* Example CAN ID: `0CF00400`
* Data Bytes: `D0 D1 D2`

---

### 5️⃣ Output Display

#### 📟 LCD1 (Raw Data)

```
S:120 T:85
F:60%
```

#### 📟 LCD2 (Encoded Data)

```
ID:0CF00400
7B 55 3C
```

---

## ▶️ How to Run

1. Open the project in **Wokwi Simulator** or upload to Raspberry Pi Pico
2. Connect components as per wiring diagram
3. Run the MicroPython code
4. Adjust potentiometers to observe real-time changes

---

## 📊 Example Output

| Speed | Temp | Fuel | Encoded Data |
| ----- | ---- | ---- | ------------ |
| 120   | 85   | 60   | 7B 55 3C     |

---

## 🧪 Applications

* Automotive embedded systems
* CAN protocol learning
* ECU simulation
* Educational demonstrations

---

## 🚀 Future Enhancements

* Full 8-byte CAN frame implementation
* Integration with MCP2515 CAN module
* TFT dashboard display
* Real vehicle sensor interfacing

---

## 📚 References

* SAE J1939 Protocol
* Raspberry Pi Pico Datasheet

---

## 👨‍💻 Author

**Vishal Meyyappan**

---

## ⭐ Acknowledgment

This project demonstrates a simplified implementation of CAN communication concepts for learning and simulation purposes.
