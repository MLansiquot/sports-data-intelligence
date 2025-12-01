import os
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score
import joblib

print("\n🏋️‍♂️ Training Win Predictor V3 (Momentum + Player Impact)\n")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "models", "win_training_v3.csv")  # <-- FIXED PATH
MODEL_OUT = os.path.join(BASE_DIR, "models", "win_predictor_v3.pkl")

# ---------------------------------------------------------
# Load Training Data
# ---------------------------------------------------------
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"\n🚨 Training dataset missing!\nExpected: {DATA_PATH}\nRun build_win_training_data_v3.py first.")

df = pd.read_csv(DATA_PATH)
print(f"📥 Loaded training dataset — {len(df):,} rows\n")

X = df.drop(columns=["HOME_WIN_LABEL"])
y = df["HOME_WIN_LABEL"]

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# ---------------------------------------------------------
# Train Model
# ---------------------------------------------------------
print("🚀 Training RandomForestClassifier...\n")

model = RandomForestClassifier(
    n_estimators=400,
    max_depth=14,
    min_samples_split=4,
    min_samples_leaf=2,
    class_weight="balanced_subsample",
    random_state=42
)

model.fit(X_train, y_train)

# ---------------------------------------------------------
# Evaluate
# ---------------------------------------------------------
preds = model.predict(X_test)
prob = model.predict_proba(X_test)[:,1]

acc = accuracy_score(y_test, preds)
auc = roc_auc_score(y_test, prob)

print(f"🔍 Model Accuracy: {acc:.3f}")
print(f"🏀 ROC–AUC Score: {auc:.3f}")

# ---------------------------------------------------------
# Save Model
# ---------------------------------------------------------
joblib.dump(model, MODEL_OUT)

print(f"\n💾 Model saved →  {MODEL_OUT}")
print("\n🔥 Win Predictor V3 Training Complete\n")
