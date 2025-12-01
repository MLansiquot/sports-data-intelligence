import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# Paths
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "data", "win_training_data.csv")
MODELS_DIR = os.path.join(PROJECT_ROOT, "models")
MODEL_PATH = os.path.join(MODELS_DIR, "win_predictor.pkl")

def train_model():
    if not os.path.exists(DATA_PATH):
        print(f"❌ Training data not found at {DATA_PATH}")
        print("   Run analytics\\build_win_training_data.py first.")
        return

    print(f"📥 Loading training data from {DATA_PATH} ...")
    df = pd.read_csv(DATA_PATH)

    # Features and label
    feature_cols = [
        "HOME_WIN_PCT",
        "AWAY_WIN_PCT",
        "HOME_STREAK",
        "AWAY_STREAK",
        "HOME_SEASON_POINTS",
        "AWAY_SEASON_POINTS",
    ]

    label_col = "HOME_WIN_FLAG"

    missing = [c for c in feature_cols + [label_col] if c not in df.columns]
    if missing:
        print("❌ Missing expected columns:", missing)
        return

    X = df[feature_cols]
    y = df[label_col]

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    # Model
    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced",
        max_depth=None
    )

    print("🤖 Training RandomForest win predictor...")
    model.fit(X_train, y_train)

    # Evaluation
    y_pred = model.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"✅ Accuracy: {acc:.3f}")
    print("\n📋 Classification Report:")
    print(classification_report(y_test, y_pred, digits=3))

    # Save model
    os.makedirs(MODELS_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\n💾 Model saved to: {MODEL_PATH}")

if __name__ == "__main__":
    train_model()
