import joblib
import networkx as nx
import pandas as pd
import warnings

# Suppress annoying sklearn multiprocessing warnings
warnings.filterwarnings("ignore", category=UserWarning)

def load_brain(model_path="models/eco_routing_model.pkl"):
    return joblib.load(model_path)

def apply_batch_green_weights(G, model):
    """
    Batch prediction: Processes all edges at once instead of one by one.
    Reduces calculation time from 10+ minutes to 0.1 seconds!
    """
    print("🌿 Extracting graph features for batch AI prediction...")
    edges = list(G.edges(keys=True, data=True))
    features_list = []
    
    for u, v, key, data in edges:
        # 1. Extract data safely
        road_length = data.get('length', 100) / 1000.0  
        
        highway_type = data.get('highway', 'residential')
        if isinstance(highway_type, list):
            highway_type = highway_type[0]
        road_type = 0 if highway_type in ['primary', 'secondary', 'trunk', 'motorway'] else 1
        
        traffic_signals = data.get('traffic_signals', 0)
        
        # Check for grade or grade_abs
        elevation_grade = data.get('grade_abs', data.get('grade', 0.0)) 
        
        traffic_volume = data.get('traffic_volume', 500) 
        
        average_speed = data.get('maxspeed', 40)
        if isinstance(average_speed, list):
            average_speed = average_speed[0]
        if isinstance(average_speed, str):
            try:
                average_speed = float(average_speed.replace(' km/h', '').strip())
            except:
                average_speed = 40.0
        
        # 2. Append to list
        features_list.append({
            'Road_Length_km': float(road_length),
            'Road_Type': int(road_type),
            'Traffic_Signals': int(traffic_signals),
            'Elevation_Grade_pc': float(elevation_grade),
            'Traffic_Volume_vph': int(traffic_volume),
            'Average_Speed_kmph': float(average_speed)
        })
        
    # 3. Create a single DataFrame and predict ALL streets at once (Super Fast)
    print(f"🧠 AI predicting CO2 for {len(features_list)} streets simultaneously...")
    df_features = pd.DataFrame(features_list)
    
    # Batch predict
    predictions = model.predict(df_features)
    
    # 4. Map the ML predictions back to the map graph
    for i, (u, v, key, data) in enumerate(edges):
        data['green_cost'] = predictions[i]
        
    print("✅ ML weights injected successfully!")
    return G