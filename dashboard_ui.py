from flask import Flask, render_template, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/state')
def get_state():
    if os.path.exists("dashboard_state.json"):
        try:
            with open("dashboard_state.json", "r") as f:
                data = json.load(f)
                return jsonify(data)
        except json.JSONDecodeError:
            return jsonify({"error": "State file updating"})
    return jsonify({"error": "State file not found"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
