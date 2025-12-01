import os
from dotenv import load_dotenv
load_dotenv()

SENSOR_ID  = os.getenv("SENSOR_ID",  "Cam_MainGate")
SENSOR_LAT = float(os.getenv("SENSOR_LAT", "34.7482"))
SENSOR_LON = float(os.getenv("SENSOR_LON", "10.7621"))
BROKER_IP  = "127.0.0.1"