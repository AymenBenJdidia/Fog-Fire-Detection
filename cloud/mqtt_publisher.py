# cloud/mqtt_publisher.py
import paho.mqtt.client as mqtt
import json
from fog_config import THINGSBOARD_HOST, THINGSBOARD_PORT, MQTT_ACCESS_TOKEN, MQTT_TOPIC

def publish_to_thingsboard(data):
    client = mqtt.Client()
    client.username_pw_set(MQTT_ACCESS_TOKEN)
    client.connect(THINGSBOARD_HOST, THINGSBOARD_PORT, 60)
    client.loop_start()
    client.publish(MQTT_TOPIC, json.dumps(data))
    client.loop_stop()