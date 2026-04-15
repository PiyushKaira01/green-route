# Green-Route: Eco-Friendly Navigation Engine

An AI-driven route optimization web application that finds eco-friendly paths by calculating carbon footprints and evaluating 3D road elevation.

## How to Run Locally

### 1. Clone the Repository
git clone https://github.com/PiyushKaira01/green-route.git
cd green-route

### 2. Set Up the Virtual Environment
**For macOS/Linux:**
python3 -m venv venv
source venv/bin/activate

### 3. Install Dependencies
pip install -r requirements.txt

### 4. Fetch the 3D City Map
python3 src/map_downloader.py

### 5. Start the Web Server
python3 web/app.py
