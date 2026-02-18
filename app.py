from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime
import requests

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return "<h1>后端服务运行正常</h1><p>请访问前端页面进行操作：<a href='http://localhost:8081'>http://localhost:8081</a></p>", 200

# 请在此处替换您的DeepSeek API Key
DEEPSEEK_API_KEY = "sk-b1a378e647de48008ad1304a7820f4d4"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

device_state = {
    "device_id": "X1-Pro-0092A",
    "is_locked": True,
    "battery": 83,
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

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    # 支持多轮对话：优先读取 history 字段（包含 role 和 content 的列表），如果为空则降级为 message
    history = data.get('history', [])
    user_message = data.get('message', '')
    
    # 如果只有 message 没有 history，构造初始 history
    if not history and user_message:
        history = [{"role": "user", "content": user_message}]
        
    if not history:
        return jsonify({"error": "No message or history provided"}), 400
        
    if DEEPSEEK_API_KEY.startswith("sk-xxxx"):
        return jsonify({"reply": "请先在 app.py 中配置有效的 DeepSeek API Key 才能使用 AI 功能。"}), 200

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    
    # 获取当前设备状态作为上下文
    current_status = "锁定" if device_state["is_locked"] else "解锁"
    system_prompt = f"""
    你是一个智能车锁系统的AI助手。
    当前设备状态：
    - 锁状态：{current_status}
    - 电量：{device_state['battery']}%
    - 信号强度：{device_state['signal']}/5
    - 经纬度：({device_state['lat']}, {device_state['lng']})
    
    你拥有控制权限。当用户要求执行特定操作时，请在回复的最后加上相应的指令代码（不要让用户看到指令代码，直接执行）：
    - 解锁车辆：[CMD:UNLOCK]
    - 锁定车辆：[CMD:LOCK]
    - 鸣笛寻车：[CMD:BEEP]
    - 导航/路径规划：[CMD:NAV:目的地名称] (例如：[CMD:NAV:天安门])
    
    注意：
    1. 如果用户改变主意想要去新的地点，请立即生成新的 [CMD:NAV:...] 指令。
    2. 请用简短、自然的语言回答用户。
    """

    # 构造请求消息列表：System Prompt + History
    # 限制 History 长度为最近 10 条，避免 Token 超限
    messages = [{"role": "system", "content": system_prompt}] + history[-10:]

    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
        response.raise_for_status()
        result = response.json()
        ai_reply = result['choices'][0]['message']['content']
        
        # 处理指令
        if "[CMD:UNLOCK]" in ai_reply:
            device_state["is_locked"] = False
            device_state["last_action_time"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            ai_reply = ai_reply.replace("[CMD:UNLOCK]", "").strip()
            
        if "[CMD:LOCK]" in ai_reply:
            device_state["is_locked"] = True
            device_state["last_action_time"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            ai_reply = ai_reply.replace("[CMD:LOCK]", "").strip()
            
        if "[CMD:BEEP]" in ai_reply:
            # 模拟鸣笛逻辑，实际可扩展
            ai_reply = ai_reply.replace("[CMD:BEEP]", "").strip()
            
        return jsonify({"reply": ai_reply})
    except Exception as e:
        print(f"DeepSeek API Error: {e}")
        return jsonify({"reply": "抱歉，AI服务暂时不可用，请稍后再试。"}), 500

if __name__ == '__main__':
    print("智能车锁后端服务启动中...")
    print("API地址: http://localhost:5000")
    print("设备数据接口: GET /api/device")
    print("锁控制接口: POST /api/control")
    app.run(debug=True, port=5000)
