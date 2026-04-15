import osmnx as ox
import networkx as nx
import folium
from pathlib import Path

def calculate_green_cost(G):
    print("🧠 Injecting 3D Elevation & ML weights into routing grid...")
    
    # These are the exact numbers learned from our Machine Learning model!
    W_LENGTH = 0.15  
    W_GRADE = 150.0   # Massive penalty for steep roads
    W_SIGNAL = 20.0  
    W_RESIDENTIAL = 10.0 
    
    for u, v, key, data in G.edges(keys=True, data=True):
        # 1. Extract physical features from the road
        length = data.get('length', 0)
        
        # OSMnx automatically generated 'grade' (which can be negative for downhill) 
        # and 'grade_abs' (absolute steepness). We use absolute steepness because 
        # both climbing a hill and braking heavily downhill ruin fuel efficiency!
        grade = data.get('grade_abs', 0.0) 
        
        highway_type = data.get('highway', 'unclassified')
        if isinstance(highway_type, list): highway_type = highway_type[0]
        
        dest_node_data = G.nodes[v]
        has_signal = 1 if dest_node_data.get('highway') == 'traffic_signals' else 0
        is_residential = 1 if 'residential' in highway_type else 0

        # 2. 🧪 THE ML EQUATION 
        # CO2 = (w1 * length) + (w2 * steepness_over_distance) + (w3 * signals)...
        predicted_emissions = (
            (length * W_LENGTH) + 
            (grade * length * W_GRADE) + 
            (has_signal * W_SIGNAL) +
            (is_residential * W_RESIDENTIAL)
        )
        
        # 3. Save the ML prediction as the new routing weight!
        data['green_cost'] = predicted_emissions

    return G

def get_eco_route_map(start_coords, end_coords):
    print("🧠 Engine triggered by web server...")
    base_dir = Path(__file__).resolve().parent.parent
    filepath = base_dir / "graphs" / "new_delhi_drive.graphml"

    if not filepath.exists():
        return "Error: Map not found. Please run downloader first."

    # Load and prep graph
    G = ox.load_graphml(filepath)
    G = calculate_green_cost(G)

    # Convert web string coordinates like "28.61, 77.22" into floats
    start_lat, start_lon = map(float, start_coords.split(','))
    end_lat, end_lon = map(float, end_coords.split(','))

    print("📍 Snapping to grid...")
    orig_node = ox.distance.nearest_nodes(G, X=start_lon, Y=start_lat)
    dest_node = ox.distance.nearest_nodes(G, X=end_lon, Y=end_lat)

    try:
        route = nx.shortest_path(G, orig_node, dest_node, weight='green_cost')
        
        print("🗺️ Generating interactive web map...")
        # FIX 1: Changed tiles to 'OpenStreetMap' for instant, reliable loading
        # ⚡ FIX 3: Using Google Maps high-speed tile servers for instant rendering
        route_map = folium.Map(
            location=[start_lat, start_lon], 
            zoom_start=14, 
            tiles='http://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}',
            attr='Google'
)
        
        # Add markers for Start and End
        folium.Marker([start_lat, start_lon], popup="Start", icon=folium.Icon(color="green")).add_to(route_map)
        folium.Marker([end_lat, end_lon], popup="Destination", icon=folium.Icon(color="red")).add_to(route_map)

        # 🌐 FIX 2: The "Google Maps" Smooth Curve Extraction
        route_coords = []
        for i in range(len(route) - 1):
            u = route[i]      # Current intersection
            v = route[i + 1]  # Next intersection
            
            # Extract the actual road (edge) connecting these two intersections
            edge_data = G.get_edge_data(u, v)[0] 
            
            if 'geometry' in edge_data:
                # If the road curves, extract every single micro-coordinate along the curve
                xs, ys = edge_data['geometry'].xy
                for x, y in zip(xs, ys):
                    route_coords.append((y, x)) # Folium requires (Lat, Lon)
            else:
                # If it's a perfectly straight street, just use the intersection point
                route_coords.append((G.nodes[u]['y'], G.nodes[u]['x']))
                
        # Append the absolute final destination node
        route_coords.append((G.nodes[route[-1]]['y'], G.nodes[route[-1]]['x']))

        # Draw the gorgeous, curve-hugging Green Route line!
        folium.PolyLine(locations=route_coords, color="#2ecc71", weight=6, opacity=0.9).add_to(route_map)

        # Save the map as an HTML string so Flask can send it to the browser
        return route_map._repr_html_()

    except nx.NetworkXNoPath:
        return "Error: No path found between these coordinates."
    except Exception as e:
        return f"Error: {str(e)}"

    except nx.NetworkXNoPath:
        return "Error: No path found between these coordinates."
    except Exception as e:
        return f"Error: {str(e)}"