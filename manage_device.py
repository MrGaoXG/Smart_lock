import os
import sys
from app import app, db, Device

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("========================================")
    print("      🚗 智能车锁数据库管理工具 🛠️")
    print("========================================")

def get_device():
    with app.app_context():
        device = Device.query.filter_by(device_id="X1-Pro-0092A").first()
        if not device:
            print("错误: 未找到设备 X1-Pro-0092A")
            return None
        return device

def show_status():
    with app.app_context():
        device = get_device()
        if not device: return
        
        print("\n📊 当前设备状态:")
        print(f"----------------------------------------")
        print(f"🆔 设备ID:   {device.device_id}")
        print(f"🔋 电量:     {device.battery}%")
        print(f"🛣️ 里程:     {device.mileage} km")
        print(f"🔒 锁定状态: {'已锁定 🔒' if device.is_locked else '已解锁 🔓'}")
        print(f"📍 经度:     {device.lng}")
        print(f"📍 纬度:     {device.lat}")
        print(f"🌡️ 温度:     {device.temp}°C")
        print(f"----------------------------------------")

def update_battery():
    try:
        val = int(input("\n请输入新的电量 (0-100): "))
        if 0 <= val <= 100:
            with app.app_context():
                device = Device.query.filter_by(device_id="X1-Pro-0092A").first()
                device.battery = val
                db.session.commit()
            print("✅ 电量更新成功！")
        else:
            print("❌ 输入无效，请输入 0-100 之间的整数")
    except ValueError:
        print("❌ 输入无效，请输入数字")

def update_mileage():
    try:
        val = float(input("\n请输入新的里程 (km): "))
        if val >= 0:
            with app.app_context():
                device = Device.query.filter_by(device_id="X1-Pro-0092A").first()
                device.mileage = val
                db.session.commit()
            print("✅ 里程更新成功！")
        else:
            print("❌ 输入无效，里程不能为负数")
    except ValueError:
        print("❌ 输入无效，请输入数字")

def update_location():
    try:
        lng = float(input("\n请输入经度 (如 116.397451): "))
        lat = float(input("请输入纬度 (如 39.909187): "))
        with app.app_context():
            device = Device.query.filter_by(device_id="X1-Pro-0092A").first()
            device.lng = lng
            device.lat = lat
            db.session.commit()
        print("✅ 位置更新成功！")
    except ValueError:
        print("❌ 输入无效，请输入数字")

def toggle_lock():
    with app.app_context():
        device = Device.query.filter_by(device_id="X1-Pro-0092A").first()
        device.is_locked = not device.is_locked
        db.session.commit()
        print(f"✅ 设备已{'锁定 🔒' if device.is_locked else '解锁 🔓'}！")

def main():
    while True:
        clear_screen()
        print_header()
        show_status()
        
        print("\n请选择操作:")
        print("1. 🔋 修改电量")
        print("2. 🛣️ 修改里程")
        print("3. 📍 修改位置")
        print("4. 🔒 切换锁定状态")
        print("5. 🚪 退出程序")
        
        choice = input("\n请输入选项 (1-5): ")
        
        if choice == '1':
            update_battery()
        elif choice == '2':
            update_mileage()
        elif choice == '3':
            update_location()
        elif choice == '4':
            toggle_lock()
        elif choice == '5':
            print("\n👋 再见！")
            break
        else:
            print("\n❌ 无效选项，请重试")
        
        input("\n按回车键继续...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 程序已终止")
