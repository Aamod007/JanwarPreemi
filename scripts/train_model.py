"""
Train a Random Forest classifier to predict pet diseases from symptoms.
Saves the model, label encoder, and feature metadata to model/.
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "pet_diseases.csv")
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "model")


def train():
    # ── Load ──────────────────────────────────────────────────────────
    df = pd.read_csv(DATA_PATH)
    print(f"Loaded dataset: {df.shape[0]} rows, {df.shape[1]} columns")

    # Features: pet_type (one-hot) + symptom columns
    symptom_cols = [c for c in df.columns if c not in ("pet_type", "disease")]

    # One-hot encode pet_type
    df_features = pd.get_dummies(df[["pet_type"]], prefix="pet", drop_first=False)
    df_features = pd.concat([df_features, df[symptom_cols]], axis=1)

    feature_names = list(df_features.columns)
    X = df_features.values
    y = df["disease"].values

    # Encode labels
    le = LabelEncoder()
    y_enc = le.fit_transform(y)

    # ── Split ─────────────────────────────────────────────────────────
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_enc, test_size=0.2, random_state=42, stratify=y_enc
    )
    print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    # ── Train ─────────────────────────────────────────────────────────
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=20,
        min_samples_split=5,
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)
    score = clf.score(X_test, y_test)
    print(f"\nTest accuracy: {score:.4f}\n")

    # ── Report ────────────────────────────────────────────────────────
    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred, target_names=le.classes_))

    # ── Save ──────────────────────────────────────────────────────────
    os.makedirs(MODEL_DIR, exist_ok=True)
    artifacts = {
        "model": clf,
        "label_encoder": le,
        "feature_names": feature_names,
        "symptom_cols": symptom_cols,
    }
    out_path = os.path.join(MODEL_DIR, "pet_disease_model.pkl")
    joblib.dump(artifacts, out_path)
    print(f"\nModel saved to {out_path}")


if __name__ == "__main__":
    train()
