import math

class ConsistentHashMap:
    def __init__(self, num_slots=512):
        self.num_slots = num_slots
        self.ring = [None] * num_slots
        self.server_map = {}

    def hash_request(self, i):
        return (i + 2*i + 17**2) % self.num_slots

    def hash_virtual(self, i, j):
        return (i + j + 2*j + 25) % self.num_slots

    def add_server(self, sid):
        k = int(math.log2(self.num_slots))
        for j in range(k):
            pos = self.hash_virtual(sid, j)
            self.ring[pos] = f"S{sid}-v{j}"
        self.server_map[sid] = True

    def remove_server(self, sid):
        k = int(math.log2(self.num_slots))
        for j in range(k):
            pos = self.hash_virtual(sid, j)
            self.ring[pos] = None
        self.server_map.pop(sid, None)

    def get_server(self, request_id):
        pos = self.hash_request(request_id)
        for i in range(self.num_slots):
            index = (pos + i) % self.num_slots
            if self.ring[index]:
                return self.ring[index].split('-')[0]  # Extract S<ID>
        return None