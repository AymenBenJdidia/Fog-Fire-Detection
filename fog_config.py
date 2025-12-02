import os
from dotenv import load_dotenv
load_dotenv()

def get_local_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        return s.getsockname()[0]
    except:
        return "127.0.0.1"


FOG_ID="Fog_2"
BROKER_IP = "192.168.1.53"               
THINGSBOARD_HOST = "demo.thingsboard.io"
THINGSBOARD_TOKEN = os.getenv("FOG_TOKEN")