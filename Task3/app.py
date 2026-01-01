from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure, OperationFailure
import pymongo
import os
import certifi
from dotenv import load_dotenv
  
load_dotenv()

app = Flask(__name__, template_folder='template')

uri = os.getenv('MONGO_URI', "mongodb+srv://Amus:1374@flask.czgznkx.mongodb.net/?appName=Flask")

# Lazy DB globals
client = None
db = None
collection = None

def init_db():
    """Initialize MongoDB connection lazily. Sets global `collection` or leaves it None on failure."""
    global client, db, collection
    if collection is not None:
        return
    try:
        client = pymongo.MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command('ping')  # Verify connection
        db = client.test
        collection = db['todo_list']
        print("✓ MongoDB connection successful")
    except Exception as e:
        print(f"✗ Connection error: {e}")
        print("Attempting with TLS disabled...")
        try:
            uri_no_tls = uri.replace("mongodb+srv://", "mongodb://")
            client = pymongo.MongoClient(uri_no_tls, tls=False)
            client.admin.command('ping')
            db = client.test
            collection = db['todo_list']
            print("✓ MongoDB connection successful (without TLS)")
        except Exception as e2:
            print(f"✗ Still failed: {e2}")
            collection = None

@app.route('/todo')
def todo_page():
    """Render the todo list page."""
    return render_template('todo.html')

@app.route('/submittodoitem', methods=['POST'])
def submit_todo_item():
    """Handle form submission for new todo items."""
    try:
        # Ensure DB initialized (lazy)
        init_db()
        if collection is None:
            return jsonify({'error': 'Database unavailable'}), 503

        item_id = request.form.get('itemID', '').strip()
        item_name = request.form.get('itemName', '').strip()
        item_description = request.form.get('itemDescription', '').strip()

        # Validate input
        if not item_id or not item_name or not item_description:
            return jsonify({'error': 'All fields (ID, name, description) are required'}), 400

        # Create and insert document
        todo_item = {
            'itemID': item_id,
            'itemName': item_name,
            'itemDescription': item_description
        }

        result = collection.insert_one(todo_item)

        return jsonify({
            'message': 'To-do item submitted successfully',
            'id': str(result.inserted_id)
        }), 201

    except OperationFailure as e:
        return jsonify({'error': 'Database operation failed'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
