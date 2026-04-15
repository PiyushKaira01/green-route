import osmnx as ox
from pathlib import Path

def download_city_map(place_name="New Delhi, Delhi, India", filename="new_delhi_drive.graphml"):
    print(f"🌍 Initiating Map Downloader for: {place_name}...")

    # 1. Professional Path Management
    # __file__ gets the location of THIS script (src/map_downloader.py)
    # .parent.parent moves us up to the main GreenRoute/ folder
    base_dir = Path(__file__).resolve().parent.parent
    graphs_dir = base_dir / "graphs"
    
    # Safety check: Ensure the graphs folder actually exists
    graphs_dir.mkdir(exist_ok=True) 
    
    filepath = graphs_dir / filename

    # 2. Check if we already downloaded it (Saves time and API limits)
    if filepath.exists():
        print(f"✅ Map already exists at: {filepath}")
        print("Skipping download. (Delete the file if you want to force a fresh download).")
        return filepath

    # 3. Download from OpenStreetMap
    print("📡 Connecting to OpenStreetMap API...")
    print("⏳ Please wait, mapping a massive city takes 1-3 minutes...")
    
    try:
        print("📡 Downloading base map from OpenStreetMap...")
        G = ox.graph_from_place(place_name, network_type='drive')
        
        print("⛰️ Calling OpenTopoData API...")
        
        u = ox.settings.elevation_url_template
        ox.settings.elevation_url_template = "https://api.opentopodata.org/v1/aster30m?locations={locations}"
        
        G = ox.elevation.add_node_elevations_google(G, batch_size=100, pause=1)
        G = ox.elevation.add_edge_grades(G)
        
        ox.settings.elevation_url_template = u
        
        print("💾 Saving map with 3D elevation data...")
        ox.save_graphml(G, filepath=filepath)
        
        print("\n✅ Download Complete with Elevation!")
        return filepath
        
    except Exception as e:
        print(f"\n❌ Error downloading map: {e}")
        return None

if __name__ == "__main__":
    # Note: If New Delhi takes too long on your Wi-Fi, change this to 
    # "Thanesar, Haryana, India" for a blazing fast test run!
    download_city_map()