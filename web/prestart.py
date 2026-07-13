"""
Runs at server startup. Ensures the ML model and the city road graph
exist locally. If they don't, downloads/regenerates them.

This script is idempotent — safe to run on every deploy.
"""
import os
import sys
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MODELS_DIR = BASE_DIR / "models"
GRAPHS_DIR = BASE_DIR / "graphs"
DATA_DIR = BASE_DIR / "data"

MODEL_PATH = MODELS_DIR / "eco_routing_model.pkl"
MODEL_URL = os.environ.get(
    "GREENROUTE_MODEL_URL",
    # Default: a placeholder. Replace with your own hosted URL (Hugging Face,
    # GitHub Releases, S3, etc.) before deploying.
    ""
)


def ensure_model():
    if MODEL_PATH.exists():
        print(f"✅ Model already present at {MODEL_PATH}")
        return

    if not MODEL_URL:
        print(
            "⚠️  No model file at models/eco_routing_model.pkl and "
            "GREENROUTE_MODEL_URL env var is not set."
        )
        print(
            "    The /route endpoint will return 503 until the model is "
            "provided. Train locally and either:"
        )
        print("      1. Set GREENROUTE_MODEL_URL to a hosted copy, or")
        print("      2. Commit the .pkl to a private repo Render can access")
        return

    print(f"📥 Downloading model from {MODEL_URL}...")
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
    print(f"✅ Model saved to {MODEL_PATH}")


def ensure_graphs_dir():
    GRAPHS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"📁 Graphs directory ready at {GRAPHS_DIR}")


if __name__ == "__main__":
    ensure_graphs_dir()
    ensure_model()
