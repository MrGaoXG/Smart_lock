from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime

app = Flask(__name__)
CORS(app)

device_state = {
    "device_id": "X1-Pro-0092A",
    "is_locked": True,
    "battery": 83,
    "signal": 4,
    "lat": 39.909187,
    "lng": 116.397451,
    "health": 92,
    "temp": 28,
    "mileage": 312.6,
    "gps_acc": 3.2,
    "day_dist": 6.40,
    "last_action_time": "2026/01/18 17:17:31",
    "sensors": {
        "motor_temp": 34.2,
        "torque": 1.2,
        "voltage": 48.2,
        "current": 0.05,
        "vibration": "Safe",
        "hall_status": "Normal",
        "activ_time": "2025/06/15",
        "total_usage": "142h 20m"
    },
    "user_info": {
        "username": "CyberRider_01",
        "role": "Administrator",
        "avatar_emoji": "👨‍🚀",
        "version": "v3.1.0 (Beta)"
    }
}

@app.route('/api/device', methods=['GET'])
def get_device():
    return jsonify(device_state)

@app.route('/api/control', methods=['POST'])
def control():
    data = request.json
    action = data.get('action')
    device_state["is_locked"] = (action == 'lock')
    device_state["last_action_time"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    return jsonify({
        "status": "success",
        "is_locked": device_state["is_locked"],
        "time": device_state["last_action_time"]
    })

if __name__ == '__main__':
    print("智能车锁后端服务启动中...")
    print("API地址: http://localhost:5000")
    print("设备数据接口: GET /api/device")
    print("锁控制接口: POST /api/control")
    app.run(debug=True, port=5000)
