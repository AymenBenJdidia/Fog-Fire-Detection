# fog_config.py
import socket
import os
from dotenv import load_dotenv

load_dotenv()   # reads .env

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        return s.getsockname()[0]
    except:
        return '127.0.0.1'

# Network
MULTICAST_GROUP = '224.0.0.251'
MULTICAST_PORT = 12345
FOG_TCP_PORT = 9999
ANNOUNCE_INTERVAL = 5

# Load balancing
MAX_CONNECTIONS_PER_FOG = 1

# ThingsBoard
THINGSBOARD_HOST = "demo.thingsboard.io"
THINGSBOARD_PORT = 1883
MQTT_ACCESS_TOKEN = os.getenv("FOG_ACCESS_TOKEN")   # ← from .env
MQTT_TOPIC = "v1/devices/me/telemetry"