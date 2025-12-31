from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

@app.route('/api', methods=['GET'])
def get_data():
    file_path = 'data.json'
    
    if not os.path.exists(file_path):
        return jsonify({"error": "Data file not found"}), 404
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid JSON in data file"}), 400

if __name__ == '__main__':
    app.run(debug=True)
