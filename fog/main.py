import json
import base64
import paho.mqtt.client as mqtt
from fog_config import BROKER_IP, get_local_ip , FOG_ID
from fog.fire_detector import detect_fire
from cloud.mqtt_publisher import publish_to_thingsboard,publish_to_thingsboard_att

def on_connect(client, userdata, flags, rc):
    print(FOG_ID ," Connected with result code:", rc)
    client.subscribe("$share/foggroup/fire/image")
    
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        
        print(f"{FOG_ID} received message from {data['sensor_id']}")
        
        if not all(k in data for k in ["image", "sensor_id", "lat", "lon"]):
            print("Invalid MQTT payload:", data)
            return

        img_bytes = base64.b64decode(data["image"])
        result = detect_fire(img_bytes)

        telemetry = {
            "fire": result["fire"],
            "confidence": result["confidence"],
            "sensor_id": data["sensor_id"],
            "sensor_lat": data["lat"],
            "sensor_lon": data["lon"],
            "fog_ip": get_local_ip(),
            "response_time": result["processing_time"]
        }
        
        attributes = {
            "fire": result["fire"],
            "confidence": result["confidence"],
            "sensor_id": data["sensor_id"]
        }

        publish_to_thingsboard(telemetry)
        
        publish_to_thingsboard_att(attributes)

        client.publish(f"fire/result/{data['sensor_id']}", json.dumps(result))

        status = "fire" if result["fire"] else "Safe"
        print(f"{data['sensor_id']} → {status} (conf: {result['confidence']})")

    except Exception as e:
        print("Fog error:", e)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER_IP, 1883, 60)
print(f"Fog ready @ {get_local_ip()} – waiting for images...")
client.loop_forever()
