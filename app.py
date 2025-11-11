# Tambahkan ini di bagian atas file app.py Anda
from flask import Flask, jsonify, render_template, request
import mysql.connector
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Fungsi helper untuk koneksi
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="iot_db"
    )

@app.route('/')
def home():
    return render_template('index.html')

# --------------------------------------------------------------------
# ENDPOINT BARU UNTUK STATISTIK (SESUAI GAMBAR ANDA)
# --------------------------------------------------------------------
@app.route('/api/statistik', methods=['GET'])
def get_statistik():
    try:
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)

        # 1. Dapatkan Statistik Umum (Max, Min, Rata-rata) untuk SUHU dan KELEMBAPAN
        cursor.execute(
            "SELECT MAX(suhu) as suhumax, MIN(suhu) as suhumin, AVG(suhu) as suhurata, "
            "MAX(humidity) as humidmax, MIN(humidity) as humidmin, AVG(humidity) as humidrata "
            "FROM data_sensor"
        )
        stats = cursor.fetchone()

        # Dapatkan nilai suhu maks untuk query berikutnya
        suhu_maksimal = stats['suhumax']

        # 2. Dapatkan Baris Data LENGKAP saat suhu sedang maks
        query_data_max = """
            SELECT id as idx, suhu as suhu, humidity as humid, lux as kecerahan, timestamp
            FROM data_sensor 
            WHERE suhu = %s
        """
        cursor.execute(query_data_max, (suhu_maksimal,))
        nilai_suhu_max_list = cursor.fetchall()

        # 3. Dapatkan Bulan dan Tahun saat suhu maks (dalam format "Bulan Tahun")
        query_month_year = """
            SELECT DISTINCT CONCAT(MONTHNAME(timestamp), ' ', YEAR(timestamp)) as month_year
            FROM data_sensor
            WHERE suhu = %s
        """
        cursor.execute(query_month_year, (suhu_maksimal,))
        month_year_max_list = cursor.fetchall()

        # 4. Susun JSON final
        response_json = {
            "suhumax": stats['suhumax'],
            "suhumin": stats['suhumin'],
            "suhurata": round(stats['suhurata'], 2),
            "humidmax": stats['humidmax'],
            "humidmin": stats['humidmin'],
            "humidrata": round(stats['humidrata'], 2),
            "nilai_suhu_max_humid_max": nilai_suhu_max_list,
            "month_year_max": month_year_max_list
        }

        cursor.close()
        db.close()
        return jsonify(response_json)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --------------------------------------------------------------------
# ENDPOINT LAMA ANDA (Boleh tetap ada)
# --------------------------------------------------------------------
'''@app.route('/sensor', methods=['GET'])
def get_sensor_data():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT id, suhu, humidity, lux, timestamp FROM data_sensor")
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(result)'''

@app.route('/insert', methods=['POST'])
def insert_data():
    data = request.json
    db = get_db_connection()
    cursor = db.cursor()
    query = "INSERT INTO data_sensor (suhu, humidity, lux) VALUES (%s, %s, %s)"
    values = (data['suhu'], data['humidity'], data['lux'])
    cursor.execute(query, values)
    db.commit()
    cursor.close()
    db.close()
    return jsonify({"message": "Data inserted"}), 201

# ---------- Run Server ----------
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)