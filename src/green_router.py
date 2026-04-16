import osmnx as ox
import networkx as nx
from pathlib import Path


def calculate_green_cost(G):
    print("🌿 Injecting 3D Elevation & ML weights into routing grid...")

    W_LENGTH = 0.15
    W_GRADE = 150.0
    W_SIGNAL = 20.0
    W_RESIDENTIAL = 10.0

    for u, v, key, data in G.edges(keys=True, data=True):
        length = data.get('length', 0)
        grade = data.get('grade_abs', 0.0)

        highway_type = data.get('highway', 'unclassified')
        if isinstance(highway_type, list): highway_type = highway_type[0]

        dest_node_data = G.nodes[v]
        has_signal = 1 if dest_node_data.get('highway') == 'traffic_signals' else 0
        is_residential = 1 if 'residential' in highway_type else 0

        predicted_emissions = (
                (length * W_LENGTH) +
                (grade * length * W_GRADE) +
                (has_signal * W_SIGNAL) +
                (is_residential * W_RESIDENTIAL)
        )
        data['green_cost'] = predicted_emissions

    return G


def get_route_data(start_query, end_query, mode="green"):
    print(f"🌍 Searching for: {start_query} -> {end_query} ({mode} mode)")

    # 1. Automatically turn text addresses into GPS coordinates!
    try:
        start_lat, start_lon = ox.geocode(start_query)
        end_lat, end_lon = ox.geocode(end_query)
    except Exception as e:
        raise ValueError("Could not find those locations. Try adding the city name (e.g., 'Taj Mahal, Agra')")

    # 2. Extract the city name to save/load the correct file
    # If user types "Gateway of India, Mumbai", we extract "Mumbai"
    city_name = start_query.split(',')[-1].strip()
    filename = f"{city_name.lower().replace(' ', '_')}_drive.graphml"

    base_dir = Path(__file__).resolve().parent.parent
    graphs_dir = base_dir / "graphs"
    graphs_dir.mkdir(exist_ok=True)
    filepath = graphs_dir / filename

    # 3. Smart Caching: Use saved map, or download it live!
    if filepath.exists():
        print(f"📁 Loading cached map for {city_name}...")
        G = ox.load_graphml(filepath)
    else:
        print(f"🌐 Downloading live map data for {city_name} (this takes ~15s)...")
        try:
            G = ox.graph_from_place(city_name, network_type='drive')
            ox.save_graphml(G, filepath)
        except Exception as e:
            raise ValueError(f"Could not download map for '{city_name}'. Ensure the city name is correct.")

    # 4. Apply our eco-weights
    G = calculate_green_cost(G)

    print("📍 Snapping to grid...")
    orig_node = ox.distance.nearest_nodes(G, X=start_lon, Y=start_lat)
    dest_node = ox.distance.nearest_nodes(G, X=end_lon, Y=end_lat)

    # 5. Calculate Route based on Mode!
    weight_attr = 'green_cost' if mode == 'green' else 'length'

    try:
        route = nx.shortest_path(G, orig_node, dest_node, weight=weight_attr)
    except nx.NetworkXNoPath:
        raise ValueError("No valid road found between these exact spots.")

    # 6. Extract smooth curves and calculate totals for the Frontend
    route_coords = []
    total_distance = 0
    total_green_cost = 0

    for i in range(len(route) - 1):
        u = route[i]
        v = route[i + 1]
        edge_data = G.get_edge_data(u, v)[0]

        total_distance += edge_data.get('length', 0)
        total_green_cost += edge_data.get('green_cost', 0)

        if 'geometry' in edge_data:
            xs, ys = edge_data['geometry'].xy
            for x, y in zip(xs, ys):
                route_coords.append([y, x])  # Leaflet format
        else:
            route_coords.append([G.nodes[u]['y'], G.nodes[u]['x']])

    route_coords.append([G.nodes[route[-1]]['y'], G.nodes[route[-1]]['x']])

    return {
        "mode": mode,
        "route": route_coords,
        "distance_m": total_distance,
        "green_cost": total_green_cost,
        "node_count": len(route)
    }