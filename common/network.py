# common/network.py
import socket
import struct
import json
import time
import numpy as np

def send_announce(message):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
    sock.sendto(json.dumps(message).encode(), ('224.0.0.251', 12345))

def listen_multicast(callback):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(('', 12345))
    mreq = struct.pack("4sl", socket.inet_aton('224.0.0.251'), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    while True:
        try:
            data, _ = sock.recvfrom(4096)
            callback(json.loads(data.decode()))
        except:
            pass

def get_simulated_gps():
    lat = 34.7260073 + np.random.uniform(-0.05, 0.05)
    lon = 10.7137492 + np.random.uniform(-0.05, 0.05)
    return round(lat, 6), round(lon, 6)