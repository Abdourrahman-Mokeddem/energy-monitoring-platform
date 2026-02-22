import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest


def detect_rolling_anomalies(df, threshold=3):
    df = df.copy()

    # Moyenne et std par heure (saisonnalité journalière)
    hourly_mean = df.groupby("hour")["energy_kwh"].transform("mean")
    hourly_std = df.groupby("hour")["energy_kwh"].transform("std")

    df["rolling_mean"] = hourly_mean
    df["rolling_std"] = hourly_std

    df["is_anomaly_rolling"] = (
        np.abs(df["energy_kwh"] - hourly_mean) >
        threshold * hourly_std
    )

    df["is_anomaly_rolling"] = df["is_anomaly_rolling"].fillna(False)

    return df


def detect_isolation_forest(df, features=None, contamination=0.1):
    df = df.copy()

    if features is None:
        features = ["energy_kwh", "hour"]

    iso_forest = IsolationForest(
        n_estimators=100,
        contamination=contamination,
        random_state=42
    )

    iso_forest.fit(df[features])

    # Score continu (plus négatif = plus anormal)
    df["iforest_score"] = iso_forest.decision_function(df[features])

    # Classification brute
    df["anomaly_iforest"] = iso_forest.predict(df[features])
    df["is_anomaly_iforest"] = df["anomaly_iforest"] == -1

    return df


# ------------------------------
# NEW STEP: Business Classification
# ------------------------------

def classify_anomalies(df):
    """
    Classify anomalies into severity levels:
    - NORMAL
    - WARNING
    - CRITICAL
    """

    df = df.copy()

    df["severity"] = "NORMAL"

    # CRITICAL = detected by both methods
    df.loc[
        df["is_anomaly_rolling"] & df["is_anomaly_iforest"],
        "severity"
    ] = "CRITICAL"

    # WARNING = detected by only one method
    df.loc[
        df["is_anomaly_rolling"] ^ df["is_anomaly_iforest"],
        "severity"
    ] = "WARNING"

    return df


def detect_anomalies(df):
    df = detect_rolling_anomalies(df)
    df = detect_isolation_forest(df)
    df = classify_anomalies(df)
    df = add_alert_levels(df)

    return df

def add_alert_levels(df):
    """
    Create hierarchical alert levels based on Isolation Forest score.
    """

    df = df.copy()

    df["alert_level"] = "NORMAL"

    # Work only on anomalies
    anomaly_scores = df.loc[df["is_anomaly_iforest"], "iforest_score"]

    if len(anomaly_scores) > 0:

        # Percentile thresholds
        critical_threshold = np.percentile(anomaly_scores, 5)
        high_threshold = np.percentile(anomaly_scores, 20)

        df.loc[df["iforest_score"] <= critical_threshold, "alert_level"] = "CRITICAL"
        df.loc[
            (df["iforest_score"] > critical_threshold) &
            (df["iforest_score"] <= high_threshold),
            "alert_level"
        ] = "HIGH"

        df.loc[
            (df["is_anomaly_iforest"]) &
            (df["alert_level"] == "NORMAL"),
            "alert_level"
        ] = "MEDIUM"

    return df