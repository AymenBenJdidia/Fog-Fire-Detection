# common/wrr_balancer.py
import threading
import time
from fog_config import MAX_CONNECTIONS_PER_FOG

class WRRBalancer:
    def __init__(self):
        self.weights = {}           # fog_id → weight
        self.current = {}           # fog_id → current counter
        self.connections = {}       # fog_id → active tasks
        self.fog_list = []          # rotation list
        self.lock = threading.Lock()
        self.last_update = 0

    def update_weights(self, loads: dict):
        if time.time() - self.last_update < 10:
            return
        with self.lock:
            new_weights = {}
            for fog_id, load in loads.items():
                # Lower load = higher weight
                weight = max(1, int(10 / (load + 1)))
                new_weights[fog_id] = weight
            self.weights = new_weights
            self.connections = {k: 0 for k in new_weights}
            self.current = {k: 0 for k in new_weights}
            # Build rotation list
            self.fog_list = []
            for fog, w in new_weights.items():
                self.fog_list.extend([fog] * w)
            self.last_update = time.time()

    def choose_fog(self):
        with self.lock:
            if not self.fog_list:
                return None
            # Filter overloaded fogs
            available = [f for f in self.fog_list if self.connections.get(f, 0) < MAX_CONNECTIONS_PER_FOG]
            if not available:
                return min(self.connections, key=self.connections.get) if self.connections else None
            selected = available[self.current.get("idx", 0) % len(available)]
            self.current["idx"] = (self.current.get("idx", 0) + 1) % len(available)
            self.connections[selected] = self.connections.get(selected, 0) + 1
            return selected

    def release(self, fog_id):
        with self.lock:
            if fog_id in self.connections:
                self.connections[fog_id] -= 1

balancer = WRRBalancer()