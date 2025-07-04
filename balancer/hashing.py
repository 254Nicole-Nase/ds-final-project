import math

class ConsistentHashMap:
    def __init__(self, num_slots=512):
        self.num_slots = num_slots
        self.ring = [None] * num_slots
        self.server_map = {}

    def hash_request(self, i):
        return (i**2 + 2*i + 17) % self.num_slots

    def hash_virtual(self, i, j):
        return (i**2 + j**2 + 2*j + 25) % self.num_slots

    def add_server(self, sid):
        k = int(math.log2(self.num_slots))
        for j in range(k):
            pos = self.hash_virtual(sid, j)
            # Linear probing for collision resolution
            original_pos = pos
            while self.ring[pos] is not None:
                pos = (pos + 1) % self.num_slots
                if pos == original_pos:
                    raise Exception("Hash ring is full!")
            self.ring[pos] = f"S{sid}-v{j}"
        self.server_map[sid] = True

    def remove_server(self, sid):
        k = int(math.log2(self.num_slots))
        for j in range(k):
            # Remove all virtual nodes for this server
            for pos in range(self.num_slots):
                if self.ring[pos] and self.ring[pos].startswith(f"S{sid}-v{j}"):
                    self.ring[pos] = None
        self.server_map.pop(sid, None)

    def get_server(self, request_id):
        pos = self.hash_request(request_id)
        for i in range(self.num_slots):
            index = (pos + i) % self.num_slots
            if self.ring[index]:
                return self.ring[index].split('-')[0]  # Extract S<ID>
        return None
