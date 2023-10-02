from flask import Flask, request, jsonify
import mysql.connector
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('.env')
load_dotenv(dotenv_path)

app = Flask(__name__)

#MySQL configuration
db = mysql.connector.connect(
    host = 'localhost',
    user = 'root',
    password = '',
    database = 'ip_management'
)

@app.route('/allocate_ip', methods=['POST'])
def allocate_ip():
    data = request.get_json()
    ip_address = data['ip_address']
    customer_name = data['customer_name']
    customer_email = data['customer_email']

    cursor = db.cursor()

    # Check if the IP address is available
    cursor.execute("SELECT id FROM ip_addresses WHERE ip_address = %s AND status = 'available'", (ip_address,))
    result = cursor.fetchone()

    if result:
        # Update the IP address status to allocated and associate with the customer
        cursor.execute("UPDATE ip_addresses SET status = 'allocated', customer_name = %s, customer_email = %s WHERE id = %s", (customer_name, customer_email, result[0]))
        db.commit()
        cursor.close()
        return jsonify({"message": "IP address allocated successfully."})
    else:
        cursor.close()
        return jsonify({"error": "IP address not available."}), 400

# def allocate_ip():
#     data = request.get_json()
#     ip_address = data['ip_address']
#     customer_name = data['customer_name']
#     customer_email = data['customer_email']

#     cursor = db.cursor()

# # Check if the IP address is available
# cursor.execute("SELECT id FROM ip_addresses WHERE ip_addresses = %s AND status = 'available'", (ip_address,))
# result = cursor.fetchone()

# if result:
#      # Update the IP address status to allocated and associate with the customer
#     cursor.execute("UPDATE ip_addresses SET status = 'allocated', customer_name = %s, customer_email = %s WHERE id = %s", (customer_name, customer_email, result[0]))
#     db.commit()
#     cursor.close()
#     return jsonify({"message": "IP address allocated successfully."})
# else:
#     cursor.close()
#     return jsonify({"error": "IP address not available."}), 400

@app.route('/release_ip/<string:ip_address>', methods=['POST'])
def release_ip(ip_address):
    cursor = db.cursor()

    # Check if the IP address is allocated
    cursor.execute("SELECT id FROM ip_addresses WHERE ip_address = %s AND status = 'allocated'", (ip_address,))
    result = cursor.fetchone()

    if result:
        # Update the IP address status to available and remove customer information
        cursor.execute("UPDATE ip_addresses SET status = 'available', customer_name = NULL, customer_email = NULL WHERE id = %s", (result[0],))
        db.commit()
        cursor.close()
        return jsonify({"message": "IP address released successfully."})
    else:
        cursor.close()
        return jsonify({"error": "IP address not allocated."}), 400

@app.route('/get_ip/<string:ip_address>', methods=['GET'])
def get_ip(ip_address):
    cursor = db.cursor()

    cursor.execute("SELECT status, customer_name, customer_email FROM ip_addresses WHERE ip_address = %s", (ip_address,))
    result = cursor.fetchone()

    if result:
        status, customer_name, customer_email = result
        cursor.close()
        return jsonify({"status": status, "customer_name": customer_name, "customer_email": customer_email})
    else:
        cursor.close()
        return jsonify({"error": "IP address not found."}), 404

if __name__ == '__main__':
    app.run(debug=True)