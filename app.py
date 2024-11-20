from flask import Flask, request, jsonify, abort
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

@app.route('/lists/<list_code>/items', methods=['POST'])
def add_item(list_code):
    data = request.get_json()
    item_name = data.get('item_name')
    quantity = data.get('quantity', 1)

    if not item_name:
        abort(400, description="Item name is required")

    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute(
        "INSERT INTO list_items (list_code, item_name, quantity) VALUES (%s, %s, %s) RETURNING *;",
        (list_code, item_name, quantity)
    )
    new_item = cursor.fetchone()
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify(new_item), 201

@app.route('/lists/<list_code>/items/<item_id>', methods=['PUT'])
def update_item(list_code, item_id):
    data = request.get_json()
    quantity = data.get('quantity')
    is_checked = data.get('is_checked')

    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)

    # Update only the fields that are provided
    update_fields = []
    update_values = []
    
    if quantity is not None:
        update_fields.append("quantity = %s")
        update_values.append(quantity)
    
    if is_checked is not None:
        update_fields.append("is_checked = %s")
        update_values.append(is_checked)

    if not update_fields:
        abort(400, description="No fields to update provided")

    update_values.append(item_id)
    update_values.append(list_code)

    cursor.execute(
        f"UPDATE list_items SET {', '.join(update_fields)} WHERE id = %s AND list_code = %s RETURNING *;",
        tuple(update_values)
    )
    
    updated_item = cursor.fetchone()
    connection.commit()
    cursor.close()
    connection.close()

    if updated_item is None:
        abort(404, description="Item not found")

    return jsonify(updated_item)

@app.route('/lists/<list_code>/items/<item_id>', methods=['DELETE'])
def delete_item(list_code, item_id):
    connection = get_db_connection()
    cursor = connection.cursor(cursor_factory=RealDictCursor)
    cursor.execute("DELETE FROM list_items WHERE id = %s AND list_code = %s RETURNING *;", (item_id, list_code))
    deleted_item = cursor.fetchone()
    connection.commit()
    cursor.close()
    connection.close()

    if deleted_item is None:
        abort(404, description="Item not found")

    return jsonify({"message": "Item deleted successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
