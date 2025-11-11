import json
import mysql.connector
import paho.mqtt.client as mqtt

# Konfigurasi database
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="iot_db"
    )

# MQTT Credentials HiveMQ
MQTT_BROKER = "5b2acd0d46e1439fb86a3928a0dd138a.s1.eu.hivemq.cloud" 
MQTT_PORT = 8883
MQTT_USER = "Device02"               
MQTT_PASS = "Device02"               
MQTT_TOPIC = "esp32/dht"

def on_connect(client, userdata, flags, rc):
    print("✅ Connected to MQTT")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
        data = json.loads(payload)

        suhu = data["suhu"]
        humidity = data["kelembapan"]

        db = get_db_connection()
        cursor = db.cursor()

        query = "INSERT INTO data_sensor (suhu, humidity) VALUES (%s, %s)"
        cursor.execute(query, (suhu, humidity))
        db.commit()

        cursor.close()
        db.close()

        print(f"✅ Data tersimpan ke DB: Suhu={suhu}, Humidity={humidity}")

    except Exception as e:
        print("❌ ERROR:", e)

client = mqtt.Client()
client.username_pw_set(MQTT_USER, MQTT_PASS)
client.tls_set()      # wajib untuk HiveMQ Cloud

client.on_connect = on_connect
client.on_message = on_message

client.connect(MQTT_BROKER, MQTT_PORT)
client.loop_forever()
