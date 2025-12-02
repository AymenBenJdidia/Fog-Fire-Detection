# sensor/main.py
import cv2
import base64
import json
import time
import paho.mqtt.client as mqtt
from sensor_config import *

client = mqtt.Client()

def on_connect(c, u, f, rc):
    print("Connected to broker with code:", rc)
    c.subscribe(f"fire/result/{SENSOR_ID}")

def on_message(c, u, msg):
    result = json.loads(msg.payload.decode())
    if result["fire"] and (result["confidence"] > 0.6) :
        print(f"\nFIRE DETECTED AT {SENSOR_ID}!")
        print("ACTIVATING WATER PUMP...\n")
    else:
        print(f"[{SENSOR_ID}] Safe – pump off")

client.on_connect = on_connect
client.on_message = on_message
client.connect(BROKER_IP, 1883, 60)
client.loop_start()

def capture():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        print("Camera error: failed to capture image.")
        return None
    _, buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
    return base64.b64encode(buf).decode()

print(f"[{SENSOR_ID}] Sensor started – located at {SENSOR_LAT}, {SENSOR_LON}")

while True:
    img = capture()
    if img is None:
        time.sleep(20)
        continue

    payload = {
        "sensor_id": SENSOR_ID,
        "image": img,
        "lat": SENSOR_LAT,
        "lon": SENSOR_LON
    }

    client.publish("fire/image", json.dumps(payload), qos=1)
    print(f"[{SENSOR_ID}] Image sent")
    time.sleep(20)
