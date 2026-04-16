import sys
from pathlib import Path
from flask import Flask, render_template, request, jsonify

# Connect to the src folder
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import your newly upgraded engine!
from src.green_router import get_route_data

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/route', methods=['POST'])
def route():
    data = request.get_json()
    start = data.get('start')
    end = data.get('end')
    mode = data.get('mode', 'green')

    try:
        # Call your actual AI routing function!
        result = get_route_data(start, end, mode)
        return jsonify(result)
    except Exception as e:
        # If a city isn't found, send the error cleanly to the frontend UI
        return jsonify({"error": str(e)}), 400


@app.route('/compare', methods=['POST'])
def compare():
    data = request.get_json()
    start = data.get('start')
    end = data.get('end')

    try:
        # Run both algorithms to compare them
        green_result = get_route_data(start, end, 'green')
        short_result = get_route_data(start, end, 'shortest')

        return jsonify({
            "green": green_result,
            "shortest": short_result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == '__main__':
    print("🚀 Booting up Green Route Web Server...")
    app.run(debug=True, port=5000)