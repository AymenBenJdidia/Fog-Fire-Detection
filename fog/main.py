# fog/main.py
import threading
import socket
import json
import time
from fog_config import *
from common.network import send_announce, listen_multicast
from common.wrr_balancer import balancer
from fog.fire_detector import detect_fire
from cloud.mqtt_publisher import publish_to_thingsboard
import base64


current_load = 0
other_fogs = {}

def announce():
    while True:
        send_announce({
            "type": "fog",
            "ip": get_local_ip(),
            "port": FOG_TCP_PORT,
            "load": current_load
        })
        time.sleep(5)

def discovery(msg):
    if msg["type"] == "fog" and msg["ip"] != get_local_ip():
        key = f"{msg['ip']}:{msg['port']}"
        other_fogs[key] = {"load": msg["load"], "last": time.time()}
        # Update WRR weights
        loads = {k: v["load"] for k, v in other_fogs.items() if time.time() - v["last"] < 15}
        loads[f"{get_local_ip()}:{FOG_TCP_PORT}"] = current_load
        balancer.update_weights(loads)

def handle_client(client):
    global current_load
    current_load += 1
    start_time = time.time()
    result = {"fire": False, "message": "Error"}
    

    try:
        data = json.loads(client.recv(1024*1024).decode())
        b64 = data["image"]

        try:
            image_bytes = base64.b64decode(b64)
        except Exception:
            raise ValueError("Invalid base64 image")

        image = image_bytes  # pass raw bytes to detect_fire
        sensor_loc = data.get("location")

        # WRR Decision
        target_fog = balancer.choose_fog()
        my_id = f"{get_local_ip()}:{FOG_TCP_PORT}"

        if target_fog and target_fog != my_id:
            ip, port = target_fog.split(':')
            with socket.socket() as fwd:
                fwd.connect((ip, int(port)))
                fwd.sendall(json.dumps(data).encode())
                result = json.loads(fwd.recv(1024*1024).decode())
            forwarded = True
        else:
            result = detect_fire(image)
            forwarded = False

        client.sendall(json.dumps(result).encode())

        # Send to ThingsBoard
        publish_to_thingsboard({
            "fire": result["fire"],
            "confidence": result["confidence"],
            "sensor_lat": sensor_loc["lat"],
            "sensor_lon": sensor_loc["lon"],
            "fog_ip": get_local_ip(),
            "response_time": round(time.time() - start_time, 2),
            "forwarded": forwarded
        })

    except Exception as e:
        print("Fog error:", e)
    finally:
        current_load -= 1
        my_id = f"{get_local_ip()}:{FOG_TCP_PORT}"
        balancer.release(my_id)
        client.close()

# Start
print(f"Fog Node → {get_local_ip()}:{FOG_TCP_PORT}")
threading.Thread(target=announce, daemon=True).start()
threading.Thread(target=listen_multicast, args=(discovery,), daemon=True).start()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(('', FOG_TCP_PORT))
server.listen(10)

while True:
    client, _ = server.accept()
    threading.Thread(target=handle_client, args=(client,), daemon=True).start()