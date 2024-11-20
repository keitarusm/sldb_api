from flask import Flask, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

def get_db_connection():
    connection = psycopg2.connect(
        host=os.getenv("DATABASE_HOST"),
        port=os.getenv("DATABASE_PORT"),
        user=os.getenv("DATABASE_USER"),
        password=os.getenv("DATABASE_PASSWORD"),
        dbname=os.getenv("DATABASE_NAME")
    )
    return connection

@app.route('/lists', methods=['POST'])
def create_list():
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute("INSERT INTO shopping_lists DEFAULT VALUES RETURNING list_code;")
    new_list = cursor.fetchone()
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify(new_list), 201

@app.route('/lists/<list_code>', methods=['GET'])
def get_list(list_code):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT * FROM list_items WHERE list_code = %s;", (list_code,))
    items = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(items)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
