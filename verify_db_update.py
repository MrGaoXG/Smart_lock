from app import app, db, Device

def verify_db_update():
    with app.app_context():
        # Get the default device
        device = Device.query.filter_by(device_id="X1-Pro-0092A").first()
        if not device:
            print("Device not found!")
            return

        print(f"Current Battery: {device.battery}%")
        print(f"Current Mileage: {device.mileage}km")

        # Modify data to prove it's connected
        device.battery = 66
        device.mileage = 666.6
        db.session.commit()

        print(f"Updated Battery to: {device.battery}%")
        print(f"Updated Mileage to: {device.mileage}km")
        print("Data successfully updated in Aliyun MySQL database.")

if __name__ == "__main__":
    verify_db_update()
