from flask import Flask, request, jsonify
import os, random, time
import requests
from hashing import ConsistentHashMap

app = Flask(__name__)

# Consistent hashing ring and server registry
ring = ConsistentHashMap()
servers = {}  # sid (int) -> container_name (str)
next_server_id = 1

DOCKER_IMAGE = "myserver"
DOCKER_NETWORK = "net1"

def add_server(container_name=None):
    global next_server_id
    sid = next_server_id
    next_server_id += 1

    if not container_name:
        container_name = f"S{sid}"

    print(f"[*] Adding server: {container_name} with ID {sid}")

    # Remove any container with the same name
    os.system(f"docker rm -f {container_name} 2>/dev/null")

    # Add to ring and server registry
    ring.add_server(sid)
    servers[sid] = container_name

    # Run the container
    os.system(
        f"docker run -d --network {DOCKER_NETWORK} --network-alias {container_name} "
        f"-e SERVER_ID={sid} --name {container_name} {DOCKER_IMAGE}"
    )

    # Let the container start
    time.sleep(2.0)

def remove_server(container_name):
    sid_to_remove = None
    for sid, name in list(servers.items()):
        if name == container_name:
            sid_to_remove = sid
            break

    if sid_to_remove is not None:
        print(f"[!] Removing server: {container_name}")
        ring.remove_server(sid_to_remove)
        os.system(f"docker stop {container_name} && docker rm {container_name}")
        del servers[sid_to_remove]
    else:
        print(f"[x] Tried to remove unknown server: {container_name}")

@app.route("/rep", methods=["GET"])
def list_replicas():
    return jsonify({
        "message": {
            "N": len(servers),
            "replicas": list(servers.values())
        },
        "status": "successful"
    }), 200

@app.route("/add", methods=["POST"])
def add_replicas():
    data = request.get_json()
    n = data.get("n", 0)
    hostnames = data.get("hostnames", [])

    if len(hostnames) > n:
        return jsonify({"message": "Too many hostnames", "status": "failure"}), 400

    for i in range(n):
        cname = hostnames[i] if i < len(hostnames) else None
        add_server(cname)

    return list_replicas()

@app.route("/rm", methods=["DELETE"])
def remove_replicas():
    data = request.get_json()
    n = data.get("n", 0)
    hostnames = data.get("hostnames", [])

    if len(hostnames) > n:
        return jsonify({"message": "Too many hostnames", "status": "failure"}), 400

    to_remove = hostnames[:]
    if len(to_remove) < n:
        available = list(set(servers.values()) - set(to_remove))
        if len(available) >= (n - len(to_remove)):
            to_remove += random.sample(available, n - len(to_remove))
        else:
            return jsonify({"message": "Not enough servers to remove", "status": "failure"}), 400

    for cname in to_remove:
        remove_server(cname)

    return list_replicas()

def try_request(target, endpoint):
    """Try to forward request to target server with retries."""
    for attempt in range(5):
        try:
            print(f"[>] Attempt {attempt+1}: http://{target}:5000{endpoint}")
            response = requests.get(f"http://{target}:5000{endpoint}", timeout=2)
            return response.json(), 200
        except Exception as e:
            print(f"[x] Error: {e}")
            time.sleep(1.5)

    # If all retries fail, remove the server
    print(f"[!] Removing unresponsive server: {target}")
    remove_server(target)
    return {
        "message": f"Server {target} was down and removed",
        "status": "failure"
    }, 500

@app.route("/", methods=["GET"])
def forward_root():
    request_id = random.randint(100000, 999999)
    target = ring.get_server(request_id)

    if not target:
        return jsonify({"message": "No servers available", "status": "failure"}), 500

    print(f"[>] Forwarding / to {target}")
    resp, code = try_request(target, "/")
    return jsonify(resp), code

@app.route("/home", methods=["GET"])
def forward_home():
    request_id = random.randint(100000, 999999)
    target = ring.get_server(request_id)

    if not target:
        return jsonify({"message": "No servers available", "status": "failure"}), 500

    print(f"[>] Forwarding /home to {target}")
    resp, code = try_request(target, "/home")
    return jsonify(resp), code

@app.route("/<path:path>", methods=["GET"])
def unknown_route(path):
    return jsonify({
        "message": f"<Error> '/{path}' endpoint does not exist in server replicas",
        "status": "failure"
    }), 404

if __name__ == "__main__":
    for _ in range(3):  # Default N = 3
        add_server()
    app.run(host="0.0.0.0", port=5000)

