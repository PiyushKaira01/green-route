import osmnx as ox
import networkx as nx
from pathlib import Path
from src.ml_integrator import load_brain, apply_batch_green_weights

# Load the AI brain into memory (we do it here so it only loads once!)
ai_brain = load_brain("models/eco_routing_model.pkl")

# Country names that must never be used as the cache key — they would force
# a full-country graph download. Match is case-insensitive.
_COUNTRY_BLOCKLIST = {
    "india", "united states", "usa", "u.s.a.", "uk", "united kingdom",
    "china", "japan", "germany", "france", "italy", "spain", "brazil",
    "russia", "canada", "australia", "mexico", "singapore", "uae",
    "saudi arabia", "south korea", "north korea", "indonesia", "turkey",
    "argentina", "pakistan", "bangladesh", "nepal", "sri lanka", "bhutan",
    "myanmar", "thailand", "vietnam", "malaysia", "philippines", "egypt",
    "nigeria", "kenya", "south africa", "new zealand", "ireland",
    "switzerland", "sweden", "norway", "finland", "denmark", "poland",
    "netherlands", "belgium", "austria", "portugal", "greece", "czechia",
    "czech republic", "hungary", "romania", "ukraine", "israel", "iran",
    "iraq", "qatar", "oman", "kuwait", "bahrain", "jordan", "lebanon",
}


def _extract_city_name(query: str) -> str:
    """
    Pick the most likely city name from a free-form query like
    'India Gate, New Delhi' or 'IIT Delhi, Delhi, India'.

    Rules:
      1. Strip a leading numeric / pin-code segment (e.g. '110001').
      2. Walk segments right-to-left, skip anything in the country blocklist
         or that looks like a country (2+ words, no spaces, generic).
      3. Skip pure-numeric segments (postal codes).
      4. Return the first non-skipped segment. Fall back to the last segment
         if everything is skipped.
    """
    parts = [p.strip() for p in query.split(",") if p.strip()]
    if not parts:
        return query.strip()

    for seg in reversed(parts):
        low = seg.lower()
        if low in _COUNTRY_BLOCKLIST:
            continue
        if seg.isdigit():
            continue
        return seg
    return parts[-1]


def calculate_green_cost(G):
    # Pass the graph and the model to the batch processor
    return apply_batch_green_weights(G, ai_brain)


def get_route_data(start_query, end_query, mode="green"):
    print(f"🌍 Searching for: {start_query} -> {end_query} ({mode} mode)")

    # 1. Automatically turn text addresses into GPS coordinates!
    try:
        start_lat, start_lon = ox.geocode(start_query)
        end_lat, end_lon = ox.geocode(end_query)
    except Exception as e:
        raise ValueError("Could not find those locations. Try adding the city name (e.g., 'Taj Mahal, Agra')")

    # 2. Extract the city name to save/load the correct file.
    # Strategy: try the last meaningful (non-country, non-numeric) segment
    # from the start query. Falling back to the last segment prevents
    # accidental full-country downloads when a query ends with "India".
    city_name = _extract_city_name(start_query)
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