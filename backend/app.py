from flask import Flask, request, jsonify
import os
import time
import random
import socket

app = Flask(__name__)

SERVER_ID = os.environ.get('SERVER_ID', 'unknown')

@app.route('/')
def home():
    processing_time = random.uniform(0.1, 0.5)
    time.sleep(processing_time)
    
    client_ip = request.remote_addr
    
    hostname = socket.gethostname()
    host_ip = socket.gethostbyname(hostname)
    
    return jsonify({
        'server_id': SERVER_ID,
        'hostname': hostname,
        'server_ip': host_ip,
        'client_ip': client_ip,
        'processing_time_ms': round(processing_time * 1000, 2),
        'status': 'healthy'
    })

@app.route('/health')
def health():
    if random.random() < 0.01:
        return jsonify({'status': 'unhealthy'}), 500
    return jsonify({'status': 'healthy'})

@app.route('/load')
def load():
    intensity = int(request.args.get('intensity', 1))
    duration = min(float(request.args.get('duration', 1)), 10.0)
    
    start_time = time.time()
    while time.time() - start_time < duration:
        for _ in range(intensity * 1000000):
            pass
    
    return jsonify({
        'server_id': SERVER_ID,
        'load_intensity': intensity,
        'duration_seconds': duration
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)