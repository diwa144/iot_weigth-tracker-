import serial
import time
import pymongo
import re
from twilio.rest import Client  # Import Twilio client

# MongoDB setup
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["iot_data"]
collection = db["weights"]

# Serial setup
SERIAL_PORT = 'COM3'  # Change this if needed
BAUD_RATE = 115200

# Twilio setup
TWILIO_ACCOUNT_SID = 'AC1023b230bf79c9c2fa49b94878a7a09b'  # Replace with your Twilio Account SID
TWILIO_AUTH_TOKEN = '9c4a5bca6c2b385b7a54b3ec96beb055'    # Replace with your Twilio Auth Token
TWILIO_PHONE_NUMBER = 'whatsapp:+14155238886'  # Twilio's WhatsApp sandbox number
TO_PHONE_NUMBER = 'whatsapp:+919994175793'  # Replace with your WhatsApp number

client_twilio = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

# Threshold weight
THRESHOLD_WEIGHT = -50.0  # Set your threshold weight in kg

def send_whatsapp_message(weight):
    """Send a WhatsApp message using Twilio."""
    message = f"⚠️ Alert! The weight has exceeded the threshold. Current weight: {weight} kg."
    try:
        client_twilio.messages.create(
            body=message,
            from_=TWILIO_PHONE_NUMBER,
            to=TO_PHONE_NUMBER
        )
        print("✅ WhatsApp message sent:", message)
    except Exception as e:
        print(f"❌ Failed to send WhatsApp message: {e}")

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Give time for the serial connection to establish
    print(f"✅ Connected to {SERIAL_PORT}")
except serial.SerialException as e:
    print(f"❌ Could not connect to {SERIAL_PORT}: {e}")
    exit()

try:
    while True:
        raw = ser.readline()
        try:
            line = raw.decode('utf-8', errors='ignore').strip()
            if line:
                print(f"📦 Received: {line}")

                # Try to extract weight from the line using regex
                match = re.search(r'-?\d+\.?\d*', line)
                if match:
                    weight = float(match.group())
                    data = {
                        'weight': weight,
                        'unit': 'kg',
                        'timestamp': time.time()
                    }

                    collection.insert_one(data)
                    print("✅ Inserted into MongoDB:", data)

                    # Check if weight exceeds the threshold
                    if weight > THRESHOLD_WEIGHT:
                        send_whatsapp_message(weight)
                else:
                    print("⚠️ No weight value found in line.")

        except Exception as e:
            print(f"❌ Error: {e}, raw data: {raw}")
except KeyboardInterrupt:
    print("\n🛑 Stopped by user")
finally:
    ser.close()
    print("🔌 Serial connection closed")

