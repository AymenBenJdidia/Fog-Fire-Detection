import socket

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        return s.getsockname()[0]
    except:
        return '127.0.0.1'



SENSOR_ID  = "SENSOR_1"
SENSOR_LAT = 35.7260073
SENSOR_LON = 10.7137492

# Network
MULTICAST_GROUP = '224.0.0.251'
MULTICAST_PORT = 12345
FOG_TCP_PORT = 9999
SEND_INTERVAL = 20