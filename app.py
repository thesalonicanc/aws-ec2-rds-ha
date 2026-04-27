import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Database configuration
db_config = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**db_config)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route('/')
def index():
    conn = get_db_connection()
    messages = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM messages ORDER BY created_at DESC")
        messages = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('index.html', messages=messages)

@app.route('/post', methods=['POST'])
def post_message():
    name = request.form.get('name')
    content = request.form.get('content')
    
    if name and content:
        conn = get_db_connection()
        if conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO messages (name, content) VALUES (%s, %s)", (name, content))
            conn.commit()
            cursor.close()
            conn.close()
            
    return redirect(url_for('index'))

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "database": "connected" if get_db_connection() else "disconnected"})

if __name__ == '__main__':
    # On EC2, we usually run with Gunicorn, but for dev:
    app.run(host='0.0.0.0', port=8080)
