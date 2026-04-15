from flask import Flask, render_template, request
import sys
from pathlib import Path

# Connect to the src folder
sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.green_router import get_eco_route_map

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/calculate_route', methods=['POST'])
def calculate_route():
    city = request.form['city']
    start = request.form['start_coords']
    end = request.form['end_coords']
    
    print(f"🌐 Web Request: {city} | {start} -> {end}")

    # Call our newly upgraded engine!
    map_html = get_eco_route_map(start, end)

    if "Error" in map_html:
        return f"<h2>⚠️ {map_html}</h2><br><a href='/'>Go Back</a>"

    # If successful, serve the interactive map full screen
    return map_html

if __name__ == '__main__':
    print("🚀 Booting up Green Route Web Server...")
    app.run(debug=True, port=5000)