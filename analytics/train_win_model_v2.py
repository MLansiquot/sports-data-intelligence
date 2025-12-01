import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    roc_auc_score,
    classification_report,
)


# -----------------------------
# Paths
# -----------------------------
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(PROJECT_ROOT, "analytics", "training_data_v2.csv")
MODEL_DIR = os.path.join(PROJECT_ROOT, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "win_predictor_v2.pkl")

os.makedirs(MODEL_DIR, exist_ok=True)


print("\n🏀 Training Win Predictor V2 (Momentum-Based Model)\n")


# -----------------------------
# Load training data
# -----------------------------
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(
        f"Training data not found at: {DATA_PATH}\n"
        "Run analytics/build_win_training_data_v2.py first."
    )

df = pd.read_csv(DATA_PATH)

required_cols = [
    "HOME_LAST10_WIN_PCT",
    "AWAY_LAST10_WIN_PCT",
    "HOME_LAST10_PTS",
    "AWAY_LAST10_PTS",
    "TARGET_WIN",
]

missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"Missing required columns in training data: {missing}")

X = df[
    [
        "HOME_LAST10_WIN_PCT",
        "AWAY_LAST10_WIN_PCT",
        "HOME_LAST10_PTS",
        "AWAY_LAST10_PTS",
    ]
]
y = df["TARGET_WIN"]

print(f"📊 Training samples: {len(df)}")
print("📐 Feature preview:")
print(X.head())
print("\n🎯 Target distribution:")
print(y.value_counts())


# -----------------------------
# Train / test split
# -----------------------------
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"\n📦 Train size: {len(X_train)}")
print(f"📦 Test size: {len(X_test)}")


# -----------------------------
# Model: Random Forest
# -----------------------------
model = RandomForestClassifier(
    n_estimators=300,
    max_depth=8,
    min_samples_split=20,
    min_samples_leaf=10,
    random_state=42,
    class_weight="balanced",
)

print("\n🚀 Training RandomForestClassifier...")
model.fit(X_train, y_train)

# -----------------------------
# Evaluation
# -----------------------------
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

acc = accuracy_score(y_test, y_pred)
try:
    auc = roc_auc_score(y_test, y_proba)
except ValueError:
    auc = None

print("\n✅ Evaluation Results:")
print(f"   • Accuracy: {acc:.4f}")
if auc is not None:
    print(f"   • ROC AUC:  {auc:.4f}")
else:
    print("   • ROC AUC:  N/A (only one class present)")

print("\n📋 Classification Report:")
print(classification_report(y_test, y_pred, digits=4))


# -----------------------------
# Save model
# -----------------------------
artifact = {
    "model": model,
    "feature_cols": list(X.columns),
}

joblib.dump(artifact, MODEL_PATH)

print(f"\n💾 Model saved to: {MODEL_PATH}")
print("\n🎉 Win Predictor V2 training complete!\n")
