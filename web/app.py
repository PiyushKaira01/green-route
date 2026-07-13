import os
import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify

# Connect to the src folder
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200


@app.route('/route', methods=['POST'])
def route():
    data = request.get_json() or {}
    start = data.get('start')
    end = data.get('end')
    mode = data.get('mode', 'green')

    if not start or not end:
        return jsonify({"error": "Both 'start' and 'end' are required."}), 400

    # Lazy-import the router so the server can boot even if model
    # loading fails. This keeps /health working for diagnosis.
    try:
        from src.green_router import get_route_data
    except Exception as e:
        return jsonify({"error": f"Router not available: {e}"}), 503

    try:
        result = get_route_data(start, end, mode)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/compare', methods=['POST'])
def compare():
    data = request.get_json() or {}
    start = data.get('start')
    end = data.get('end')

    if not start or not end:
        return jsonify({"error": "Both 'start' and 'end' are required."}), 400

    try:
        from src.green_router import get_route_data
    except Exception as e:
        return jsonify({"error": f"Router not available: {e}"}), 503

    try:
        green_result = get_route_data(start, end, 'green')
        short_result = get_route_data(start, end, 'shortest')
        return jsonify({"green": green_result, "shortest": short_result})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    # Local dev: python web/app.py  →  http://localhost:5000
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    print(f"🚀 Booting up Green Route Web Server on port {port} (debug={debug})...")
    app.run(host="0.0.0.0", port=port, debug=debug)