import paho.mqtt.client as mqtt
import json
from fog_config import THINGSBOARD_HOST, THINGSBOARD_TOKEN

client = mqtt.Client()
client.username_pw_set(THINGSBOARD_TOKEN)
client.connect(THINGSBOARD_HOST, 1883, 60)
client.loop_start()

def publish_to_thingsboard(data):
    client.publish("v1/devices/me/telemetry", json.dumps(data))