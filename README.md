# 🛡️ ResilNet — Environmental Intelligence & Multi-Hazard Network

> **Smart India Hackathon (SIH)**  
> **Problem Statement ID:** 26178  
> **Problem Statement Title:** A resilient, AI-powered environmental monitoring network that provides early detection, localized intelligence, and actionable alerts for floods, forest fires, pollution events, and other environmental hazards common in India.  
> **Organization:** Qualcomm Inc  
> **Category:** Hardware | **Theme:** Disaster Management  

---

## 📋 Problem Statement & Background

India faces a growing range of environmental and climate-related risks including urban flooding, river floods, cyclones, forest fires, air pollution, extreme heat, and landslides. Traditional monitoring systems often depend on centralized infrastructure and may fail or suffer from high latency during localized disasters.

**ResilNet** is a distributed Environmental Intelligence Network designed for early detection and proactive risk prevention. By leveraging **On-Device Edge AI**, sensor nodes process data locally to reduce latency, minimize bandwidth, and continue operating during total network blackouts—transmitting only verified, high-priority alerts to authorities and communities.

---

## 💡 Core System Features

1. **Distributed Smart Sensor Nodes:** ESP32-based multi-sensor nodes monitoring water levels, rainfall, temperature, humidity, smoke, air quality, soil moisture, and vibration.
2. **On-Device & Gateway AI Analytics:** Local anomaly detection and OpenCV computer vision for wildfire and flood risk verification without continuous cloud reliance.
3. **Multi-Hazard Early Warning Dashboard:** Real-time web command center built with Python, WebSockets, Tailwind CSS, Chart.js, and Leaflet GIS mapping.
4. **Human Ground Intelligence (HGI):** Crowdsourced ground reporting integration to validate edge warnings in real time.
5. **Resilient Offline Architecture:** Operates over low-power, offline mesh/direct protocols (ESP-NOW/LoRa) ensuring continuous uptime.

---

## 💻 Tech Stack

* **Hardware:** ESP32, ESP32-CAM, Ultrasonic (HC-SR04), DHT22, MQ Sensors, SW-420 Vibration Sensor
* **Backend:** Python 3 (WebSockets, PySerial, OpenCV, NumPy)
* **Frontend:** HTML5, Tailwind CSS, Chart.js, Leaflet.js
* **Version Control:** Git, GitHub

---

## 🚀 Quick Setup & Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/moulyaraj/ResilNet_Dashboard.git](https://github.com/moulyaraj/ResilNet_Dashboard.git)
cd ResilNet_Dashboard
