import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import os

def train_eco_model():
    print("🚀 Initializing Green-Route AI Training Sequence...\n")

    # 1. Load the Dataset
    filepath = "data/continuous_eco_dataset.csv"
    if not os.path.exists(filepath):
        print(f"❌ Error: Could not find {filepath}. Did you run the generator?")
        return
        
    df = pd.read_csv(filepath)
    print(f"📊 Dataset loaded successfully. Shape: {df.shape}")

    # 2. Data Preprocessing
    # Machine Learning models only understand numbers, so we convert the text column
    df['Road_Type'] = df['Road_Type'].map({'Main_Artery': 0, 'Residential': 1})

    # Define X (The Features / Inputs) and y (The Target / Output)
    X = df[['Road_Length_km', 'Road_Type', 'Traffic_Signals', 'Elevation_Grade_pc', 'Traffic_Volume_vph', 'Average_Speed_kmph']]
    y = df['CO2_Emissions_g']

    # Split into 80% Training Data and 20% Testing Data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    print(f"✂️ Data split: {len(X_train)} training rows, {len(X_test)} testing rows.")

    # 3. Initialize and Train the Model
    print("\n🧠 Training Random Forest Regressor (This might take a few seconds)...")
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)

    # 4. Evaluate the Model (Testing it on data it has never seen before)
    predictions = model.predict(X_test)
    
    mse = mean_squared_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    print("\n📈 Model Evaluation Metrics:")
    print(f"   - Mean Squared Error (MSE): {mse:.2f}")
    print(f"   - R-Squared Accuracy Score: {r2 * 100:.2f}%")

    # 5. Save the Trained Brain
    os.makedirs('models', exist_ok=True)
    model_path = "models/eco_routing_model.pkl"
    joblib.dump(model, model_path)
    
    print(f"\n✅ Success! Trained AI model saved securely to: {model_path}")

if __name__ == "__main__":
    train_eco_model()