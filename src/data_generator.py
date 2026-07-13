import pandas as pd
import numpy as np
import os

def generate_continuous_eco_dataset(num_samples=10000):
    print("🌍 Initializing Upgraded Physics-Based Data Generator...")
    
    np.random.seed(42) 
    
    # 1. Generate Core Geometrics
    road_length = np.random.uniform(0.2, 15.0, num_samples)
    
    elevation_grade = np.random.normal(2.0, 3.0, num_samples) 
    elevation_grade = np.clip(elevation_grade, -5.0, 15.0)
    
    # 2. Re-introduce Road Type
    # 60% chance of Main Artery, 40% chance of Residential
    road_type = np.random.choice(['Main_Artery', 'Residential'], num_samples, p=[0.6, 0.4])
    
    # 3. Calculate Traffic Signals based on Road Length and Type
    # Main Arteries: ~0.5 signals per km. Residential: ~2.0 signals per km.
    signals_per_km = np.where(road_type == 'Main_Artery', 0.5, 2.0)
    traffic_signals = np.round(road_length * signals_per_km + np.random.normal(0, 1, num_samples)).astype(int)
    traffic_signals = np.maximum(traffic_signals, 0) # No negative signals
    
    # 4. Traffic Volume
    traffic_volume = np.random.randint(100, 3000, num_samples)
    
    # 5. Physics Calculation: Average Speed
    # Main Arteries start at 60km/h, Residential starts at 40km/h
    base_speed = np.where(road_type == 'Main_Artery', 60, 40)
    
    # Penalties: Volume, Steepness, and stopping at Signals
    speed_kmph = base_speed - (traffic_volume / 100) - (np.abs(elevation_grade) * 1.5) - (traffic_signals * 0.5)
    speed_kmph = np.clip(speed_kmph + np.random.normal(0, 3, num_samples), 10, 80)
    
    # 6. Physics Calculation: CO2 Emissions (grams)
    # Base: 120g per km
    base_emissions = road_length * 120 
    
    # Grade Penalty
    grade_factor = np.where(elevation_grade > 0, 1 + (elevation_grade * 0.15), 1 + (elevation_grade * 0.05))
    
    # Congestion Penalty
    speed_factor = np.where(speed_kmph < 30, 1.5, 1.0)
    
    # Signal Penalty: Adding a flat ~15g of CO2 per traffic signal (idling + accelerating)
    signal_penalty = traffic_signals * 15.0
    
    # Final Math + Real-world noise
    raw_co2 = (base_emissions * grade_factor * speed_factor) + signal_penalty
    noise = np.random.normal(0, raw_co2 * 0.05) 
    final_co2_emissions = raw_co2 + noise
    
    # 7. Assemble the final Master Dataset
    df = pd.DataFrame({
        'Road_Length_km': np.round(road_length, 3),
        'Road_Type': road_type,
        'Traffic_Signals': traffic_signals,
        'Elevation_Grade_pc': np.round(elevation_grade, 2),
        'Traffic_Volume_vph': traffic_volume,
        'Average_Speed_kmph': np.round(speed_kmph, 1),
        'CO2_Emissions_g': np.round(np.maximum(final_co2_emissions, 50), 2) 
    })
    
    # Save it
    os.makedirs('data', exist_ok=True)
    filepath = "data/continuous_eco_dataset.csv"
    df.to_csv(filepath, index=False)
    
    print(f"\n✅ Success! 10,000 comprehensive rows saved to {filepath}")
    print(df.head(10))

if __name__ == "__main__":
    generate_continuous_eco_dataset()