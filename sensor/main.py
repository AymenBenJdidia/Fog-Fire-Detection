# sensor/main.py
import threading
import socket
import time
import cv2
import base64
from common.network import listen_multicast, send_announce
from sensor_config import *
import json

fogs = {}

def discovery(msg):
    if msg["type"] == "fog":
        key = f"{msg['ip']}:{msg['port']}"
        fogs[key] = time.time()

def measure_latency(ip, port):
    try:
        start = time.time()
        s = socket.socket()
        s.settimeout(0.4)
        s.connect((ip, port))
        s.close()
        return time.time() - start
    except:
        return 999
    
def pick_best_fog():
    best_key = None
    best_latency = 999

    for key in fogs:
        ip, port = key.split(":")
        port = int(port)

        lat = measure_latency(ip, port)
        print(f"Latency to {ip}:{port} = {lat*1000:.1f} ms")

        if lat < best_latency:
            best_latency = lat
            best_key = key

    return best_key



def capture():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        frame = cv2.imread("test_fire.jpg") or np.zeros((480,640,3), dtype=np.uint8)
    _, buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 65])
    return base64.b64encode(buf).decode()


def send_loop():
    while True:
        time.sleep(0)
        if not fogs:
            print("No fog found...")
            continue

        best = pick_best_fog()
        
        
        if not best:
            print("No fog available")
            continue
        
        print("found fogs ",fogs)
        ip, port = best.split(':')

        try:
            img = capture()
            print(f"[{SENSOR_ID}] Sending from fixed location: {SENSOR_LAT}, {SENSOR_LON}")
            payload = json.dumps({
                "image": img,
                "location": {"lat": SENSOR_LAT, "lon": SENSOR_LON},
                "sensor_id": SENSOR_ID
            }).encode()

            s = socket.socket()
            s.connect((ip, int(port)))
            s.sendall(payload)
            result = json.loads(s.recv(1024).decode())
            s.close()

            print(f"Result: {result['message']} (Confidence: {result['confidence']})")

            # FIRE DETECTED → ACTIVATE WATER PUMP!
            if result["fire"] and result['confidence'] > 0.7:
                print("FIRE DETECTED! ACTIVATING WATER PUMP NOW!")
                print("PUMP ON – Extinguishing fire...")
            else:
                print("No fire – Pump remains OFF")

        except Exception as e:
            print("Send failed:", e)

print("Sensor starting...")
threading.Thread(target=listen_multicast, args=(discovery,), daemon=True).start()
time.sleep(3)
threading.Thread(target=send_loop, daemon=True).start()
input("Press Enter to stop...\n")