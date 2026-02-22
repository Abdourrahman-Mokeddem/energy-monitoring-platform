import pandas as pd

def preprocess_energy_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and enrich raw energy data.
    - Converts timestamp to datetime
    - Extracts hour of day
    - Identifies night periods (22h–6h)
    """

    df = df.copy()

    # Safe datetime conversion
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    # Time features
    df["hour"] = df["timestamp"].dt.hour

    # Night period definition: 22h–6h
    df["is_night"] = (df["hour"] < 6) | (df["hour"] >= 22)

    return df
