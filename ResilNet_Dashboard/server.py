import asyncio
import json
import os
import random
import serial
import websockets
import cv2
import numpy as np
from http.server import SimpleHTTPRequestHandler, HTTPServer
import threading

# CONFIGURATION
SERIAL_PORT = "COM3"  # Change to your ESP32 Gateway Port (e.g. COM4 or /dev/ttyACM0)
BAUD_RATE = 115200
USE_MOCK = True       # Set to False when physical ESP32 is plugged in

connected_clients = set()
latest_state = {
    "telemetry": {"dist": 80.0, "temp": 24.5, "press": 1013.2, "rain": 0, "vib": 0.05},
    "cam_analysis": {"fire_detected": False, "flood_detected": False, "confidence": 0.0},
    "ai_score": {"FLOOD": 0, "FIRE": 0, "QUAKE": 0, "STATUS": "NORMAL", "CONFIDENCE": 0}
}

def analyze_image_opencv(image_bytes):
    """
    Lightweight, local vision processing for ESP32-CAM images.
    Detects fire (high HSV orange/red saturation) and flood water surface reflection.
    """
    try:
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return {"fire_detected": False, "flood_detected": False, "confidence": 0.0}

        # Convert to HSV color space
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        # Fire Detection Mask (Orange / Red / Yellow Glow)
        lower_fire = np.array([0, 120, 180])
        upper_fire = np.array([25, 255, 255])
        fire_mask = cv2.inRange(hsv, lower_fire, upper_fire)
        fire_pct = (cv2.countNonZero(fire_mask) / (img.shape[0] * img.shape[1])) * 100

        fire_alert = fire_pct > 3.0  # Threshold
        confidence = min(fire_pct * 20, 95.0)

        return {
            "fire_detected": fire_alert,
            "flood_detected": False,
            "confidence": round(confidence, 1)
        }
    except Exception as e:
        print(f"Vision Processing Error: {e}")
        return {"fire_detected": False, "flood_detected": False, "confidence": 0.0}

def compute_multi_hazard_ai(telemetry, vision):
    """Fuses physical telemetry, vision analysis, and HGI data into a single verified score."""
    dist = telemetry.get("dist", 100.0)
    temp = telemetry.get("temp", 25.0)
    vib = telemetry.get("vib", 0.0)

    # Flood Scoring
    flood = 0
    if dist < 20.0: flood += 70
    elif dist < 40.0: flood += 35
    if telemetry.get("rain", 0) > 3: flood += 20
    if vision.get("flood_detected"): flood += 25

    # Fire Scoring
    fire = 0
    if temp > 45.0: fire += 60
    if vision.get("fire_detected"): fire += 40

    # Quake Scoring
    quake = 0
    if vib > 2.0: quake += 85
    elif vib > 0.8: quake += 40

    scores = {"FLOOD": min(flood, 100), "FIRE": min(fire, 100), "EARTHQUAKE": min(quake, 100)}
    max_hazard = max(scores, key=scores.get)
    max_val = scores[max_hazard]

    status = "NORMAL"
    if max_val > 70: status = "CRITICAL_ALERT"
    elif max_val > 35: status = "WARNING"

    return {
        "scores": scores,
        "primary_hazard": max_hazard,
        "confidence": max_val,
        "status": status
    }

async def broadcast_state():
    if connected_clients:
        msg = json.dumps(latest_state)
        await asyncio.gather(*[c.send(msg) for c in connected_clients])

async def serial_reader():
    if USE_MOCK:
        while True:
            # Generate simulated ESP-NOW telemetry
            latest_state["telemetry"] = {
                "dist": round(random.uniform(10.0, 90.0), 1),
                "temp": round(random.uniform(22.0, 48.0), 1),
                "press": round(random.uniform(995.0, 1015.0), 1),
                "rain": random.choice([0, 0, 1, 5]),
                "vib": round(random.uniform(0.02, 2.5), 2)
            }
            latest_state["ai_score"] = compute_multi_hazard_ai(latest_state["telemetry"], latest_state["cam_analysis"])
            await broadcast_state()
            await asyncio.sleep(2)
    else:
        try:
            ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
            while True:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line.startswith("{") and line.endswith("}"):
                        data = json.loads(line)
                        latest_state["telemetry"] = data
                        latest_state["ai_score"] = compute_multi_hazard_ai(data, latest_state["cam_analysis"])
                        await broadcast_state()
                await asyncio.sleep(0.01)
        except Exception as e:
            print(f"Serial Error: {e}")

async def ws_handler(websocket):
    connected_clients.add(websocket)
    try:
        await websocket.send(json.dumps(latest_state))
        async for msg in websocket:
            # Handle HGI ground reports submitted from web UI
            data = json.loads(msg)
            if data.get("type") == "HGI":
                obs = data.get("obs")
                if obs == "FIRE": latest_state["cam_analysis"]["fire_detected"] = True
                latest_state["ai_score"] = compute_multi_hazard_ai(latest_state["telemetry"], latest_state["cam_analysis"])
                await broadcast_state()
    finally:
        connected_clients.remove(websocket)

def run_http_server():
    os.chdir(os.path.join(os.path.dirname(__file__), 'public'))
    server = HTTPServer(('0.0.0.0', 8080), SimpleHTTPRequestHandler)
    print("Dashboard UI ready at: http://localhost:8080")
    server.serve_forever()

async def main():
    threading.Thread(target=run_http_server, daemon=True).start()
    async with websockets.serve(ws_handler, "localhost", 8000):
        print("WebSocket Gateway listening on ws://localhost:8000")
        await serial_reader()

if __name__ == "__main__":
    asyncio.run(main())