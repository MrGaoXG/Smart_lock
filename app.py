from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import datetime
import requests
import json
import os

app = Flask(__name__)
CORS(app)
#
# ==========================================
# 数据库配置 (Database Configuration)
# ==========================================
# 默认使用本地 SQLite 数据库以便快速演示
# 如果要连接阿里云 MySQL，请取消注释并填写以下信息：
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:YOUR_PASSWORD@YOUR_ALIYUN_IP:3306/car_lock_db'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'local_device.db')
                   
# 配置 MySQL 连接 (阿里云)
# 注意：生产环境建议将密码放在环境变量中
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://vehicle_user:GZX2005616@121.43.138.178/vehicle_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ==========================================
# 数据模型 (Data Model)
# ==========================================
class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(50), unique=True, nullable=False)
    is_locked = db.Column(db.Boolean, default=True)
    battery = db.Column(db.Integer, default=100)
    signal_strength = db.Column(db.Integer, default=5)
    lat = db.Column(db.Float, default=39.909187)
    lng = db.Column(db.Float, default=116.397451)
    health = db.Column(db.Integer, default=100)
    temp = db.Column(db.Float, default=25.0)
    mileage = db.Column(db.Float, default=0.0)
    gps_acc = db.Column(db.Float, default=5.0)
    day_dist = db.Column(db.Float, default=0.0)
    last_action_time = db.Column(db.String(50))
    
    # 存储复杂对象的 JSON 字符串
    sensors_json = db.Column(db.Text) 
    user_info_json = db.Column(db.Text)

    def to_dict(self):
        return {
            "device_id": self.device_id,
            "is_locked": self.is_locked,
            "battery": self.battery,
            "signal": self.signal_strength,
            "lat": self.lat,
            "lng": self.lng,
            "health": self.health,
            "temp": self.temp,
            "mileage": self.mileage,
            "gps_acc": self.gps_acc,
            "day_dist": self.day_dist,
            "last_action_time": self.last_action_time,
            "sensors": json.loads(self.sensors_json) if self.sensors_json else {},
            "user_info": json.loads(self.user_info_json) if self.user_info_json else {}
        }

# ==========================================
# 数据库初始化 (Database Initialization)
# ==========================================
def init_db():
    with app.app_context():
        db.create_all()
        # 如果没有设备数据，插入默认数据
        if not Device.query.filter_by(device_id="X1-Pro-0092A").first():
            default_device = Device(
                device_id="X1-Pro-0092A",
                is_locked=True,
                battery=83,
                signal_strength=4,
                lat=39.909187,
                lng=116.397451,
                health=92,
                temp=28,
                mileage=312.6,
                gps_acc=3.2,
                day_dist=6.40,
                last_action_time="2026/01/18 17:17:31",
                sensors_json=json.dumps({
                    "motor_temp": 34.2,
                    "torque": 1.2,
                    "voltage": 48.2,
                    "current": 0.05,
                    "vibration": "Safe",
                    "hall_status": "Normal",
                    "activ_time": "2025/06/15",
                    "total_usage": "142h 20m"
                }),
                user_info_json=json.dumps({
                    "username": "CyberRider_01",
                    "role": "Administrator",
                    "avatar_emoji": "👨‍🚀",
                    "version": "v3.1.0 (Beta)"
                })
            )
            db.session.add(default_device)
            db.session.commit()
            print("初始化默认设备数据成功")

# 初始化数据库
init_db()

@app.route('/')
def index():
    return "<h1>后端服务运行正常</h1><p>请访问前端页面进行操作：<a href='http://localhost:8081'>http://localhost:8081</a></p>", 200

# 请在此处替换您的DeepSeek API Key
DEEPSEEK_API_KEY = "sk-b1a378e647de48008ad1304a7820f4d4"
DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

@app.route('/api/device', methods=['GET'])
def get_device():
    device = Device.query.filter_by(device_id="X1-Pro-0092A").first()
    if device:
        return jsonify(device.to_dict())
    return jsonify({"error": "Device not found"}), 404

@app.route('/api/control', methods=['POST'])
def control():
    data = request.json
    action = data.get('action')
    
    device = Device.query.filter_by(device_id="X1-Pro-0092A").first()
    if not device:
        return jsonify({"error": "Device not found"}), 404

    is_locked = (action == 'lock')
    device.is_locked = is_locked
    device.last_action_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    
    db.session.commit()
    
    return jsonify({
        "status": "success",
        "is_locked": device.is_locked,
        "time": device.last_action_time
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
    device = Device.query.filter_by(device_id="X1-Pro-0092A").first()
    if not device:
        current_status = "未知"
        battery = 0
        signal = 0
        lat, lng = 0, 0
        health = 0
        temp = 0
        mileage = 0
        user_name = "访客"
    else:
        current_status = "锁定" if device.is_locked else "解锁"
        battery = device.battery
        signal = device.signal_strength
        lat, lng = device.lat, device.lng
        health = device.health
        temp = device.temp
        mileage = device.mileage
        
        # 获取用户信息用于个性化称呼
        try:
            user_info = json.loads(device.user_info_json) if device.user_info_json else {}
            user_name = user_info.get("username", "尊贵的车主")
        except:
            user_name = "尊贵的车主"

    # 获取实时时间和天气
    current_time = datetime.datetime.now().strftime("%Y年%m月%d日 %H:%M:%S %A")
    
    # 尝试获取天气 (使用 wttr.in 免费接口，1秒超时避免卡顿)
    weather_info = "天气数据获取中..." 
    try:
        # format=%C+%t => Condition + Temp (e.g. "Sunny +25°C")
        # lang=zh => 中文
        w_url = f"https://wttr.in/{lat},{lng}?format=%C+%t&lang=zh"
        w_res = requests.get(w_url, timeout=1.0)
        if w_res.status_code == 200:
            weather_info = w_res.text.strip()
    except:
        weather_info = "暂时无法获取天气"

    system_prompt = f"""
    你是一个极具科技感、贴心的智能车锁系统AI管家（代号：DeepRider）。
    你正在服务的主人是：{user_name}。
    
    【环境与时间】
    - 🕒 当前时间：{current_time}
    - 🌤️ 当地天气：{weather_info}
    
    【实时车辆遥测数据】
    - 🔒 锁状态：{current_status}
    - 🔋 电量：{battery}% (电量低于20%时请务必提醒用户充电)
    - 📡 信号：{signal}/5
    - 📍 坐标：({lat}, {lng})
    - ❤️ 健康度：{health}% (低于80%时建议预约保养)
    - 🌡️ 车内温度：{temp}°C
    - 🛣️ 总里程：{mileage} km
    
    【你的核心能力】
    你不仅能陪用户聊天，还能直接控制车辆。当意图明确时，请在回复末尾附加指令代码（用户不可见，系统会自动执行）：
    1. 🔓 解锁：[CMD:UNLOCK]
    2. 🔒 落锁：[CMD:LOCK]
    3. 📢 寻车/鸣笛：[CMD:BEEP]
    4. 🗺️ 导航：[CMD:NAV:目的地] (例如：[CMD:NAV:首都机场])
    
    【智能交互准则】
    1. **主动关怀**：如果车内温度过高(>35°C)，提醒用户注意散热；如果电量低，主动建议寻找充电桩。
    2. **导航响应**：当用户说“去某地”、“导航到某地”时，务必生成 [CMD:NAV:...] 指令。如果用户更改目的地，立即生成新指令。
    3. **状态感知**：如果用户问“车在哪里”，请根据坐标回答（例如：“车辆目前定位在经度{lng}，纬度{lat}附近”）。
    4. **风格设定**：请用简洁、专业但略带幽默的口吻回复，像钢铁侠的JARVIS一样。不要长篇大论。
    
    现在，请根据用户的输入和当前车辆状态进行回复。
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
        action_taken = False
        if "[CMD:UNLOCK]" in ai_reply:
            if device:
                device.is_locked = False
                device.last_action_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                action_taken = True
            ai_reply = ai_reply.replace("[CMD:UNLOCK]", "").strip()
            
        if "[CMD:LOCK]" in ai_reply:
            if device:
                device.is_locked = True
                device.last_action_time = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
                action_taken = True
            ai_reply = ai_reply.replace("[CMD:LOCK]", "").strip()
            
        if "[CMD:BEEP]" in ai_reply:
            # 模拟鸣笛逻辑，实际可扩展
            ai_reply = ai_reply.replace("[CMD:BEEP]", "").strip()
        
        if action_taken:
            db.session.commit()
            
        return jsonify({"reply": ai_reply})
    except Exception as e:
        print(f"DeepSeek API Error: {e}")
        return jsonify({"reply": "抱歉，AI服务暂时不可用，请稍后再试。"}), 500


if __name__ == '__main__':
    print("智能车锁后端服务启动中...")
    print("API地址: http://localhost:5000")
    print("设备数据接口: GET /api/device")
    print("锁控制接口: POST /api/control")
    app.run(debug=True, host='0.0.0.0', port=5000)
