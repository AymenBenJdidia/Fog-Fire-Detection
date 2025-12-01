# fog/main.py  ← FINAL FIXED VERSION
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


def safe_recv(sock, timeout=5):
    """Receive all data until we get a complete JSON (prevents partial recv)"""
    sock.settimeout(timeout)
    data = b""
    while True:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            data += chunk
            # Small JSON result → stop when we see closing brace/bracket
            if len(data) > 20 and (data.endswith(b'}') or data.endswith(b']')):
                break
        except socket.timeout:
            break
        except:
            break
    return data


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
        loads = {k: v["load"] for k, v in other_fogs.items() if time.time() - v["last"] < 15}
        loads[f"{get_local_ip()}:{FOG_TCP_PORT}"] = current_load
        balancer.update_weights(loads)


def handle_client(client):
    global current_load
    current_load += 1
    start_time = time.time()
    result = {"fire": False, "message": "Error", "confidence": 0.0}
    forwarded = False

    try:
        raw = safe_recv(client)
        data = json.loads(raw.decode())

        image_bytes = base64.b64decode(data["image"])
        sensor_loc = data.get("location", {"lat": 34.75, "lon": 10.76})
        sensor_id = data.get("sensor_id", "Unknown")

        target_fog = balancer.choose_fog()
        my_id = f"{get_local_ip()}:{FOG_TCP_PORT}"

        if target_fog and target_fog != my_id:
            ip, port = target_fog.split(':')
            with socket.socket() as fwd:
                fwd.connect((ip, int(port)))
                fwd.sendall(raw) 
                result_raw = safe_recv(fwd)          
                result = json.loads(result_raw.decode())
            forwarded = True
        else:
            result = detect_fire(image_bytes)
            forwarded = False

        # Send result back to sensor
        client.sendall(json.dumps(result).encode())
        time.sleep(0.01) 

        publish_to_thingsboard({
            "fire": result["fire"],
            "confidence": result.get("confidence", 0.0),
            "sensor_lat": sensor_loc["lat"],
            "sensor_lon": sensor_loc["lon"],
            "sensor_id": sensor_id,
            "fog_ip": get_local_ip(),
            "response_time": round(time.time() - start_time, 2),
            "forwarded": forwarded
        })

    except Exception as e:
        print("Fog error:", e)
    finally:
        current_load -= 1
        balancer.release(f"{get_local_ip()}:{FOG_TCP_PORT}")
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