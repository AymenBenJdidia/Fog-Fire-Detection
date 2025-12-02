import paho.mqtt.client as mqtt
import json
from fog_config import THINGSBOARD_HOST, THINGSBOARD_TOKEN

client = mqtt.Client()

# Authentication
client.username_pw_set(THINGSBOARD_TOKEN)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to ThingsBoard")
    else:
        print("ThingsBoard connection failed, code:", rc)

client.on_connect = on_connect

# Connect to ThingsBoard MQTT service
client.connect(THINGSBOARD_HOST, 1883, 60)
client.loop_start()

def publish_to_thingsboard(data):
    payload = json.dumps(data)
    result = client.publish("v1/devices/me/telemetry", payload, qos=1)

    if result.rc != 0:
        print("TB publish failed with code:", result.rc)



def publish_to_thingsboard_att(data):
    payload = json.dumps(data)
    result = client.publish("v1/devices/me/attributes", payload, qos=1)
