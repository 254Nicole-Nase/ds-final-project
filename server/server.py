from flask import Flask, jsonify
import os

app = Flask(__name__)
SERVER_ID = os.getenv("SERVER_ID", "unknown")
REQUEST_COUNT = 0  # Add this line

@app.route("/home", methods=["GET"])
def home():
    global REQUEST_COUNT  # Declare as global
    REQUEST_COUNT += 1    # Increment the counter
    return jsonify({
        "message": f"Hello from Server: {SERVER_ID}",
        "status": "successful",
        "request_count": REQUEST_COUNT  # Add this to the response
    }), 200

@app.route("/heartbeat", methods=["GET"])
def heartbeat():
    return '', 200 #OK status

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
