import pandas as pd
import metrics as mt

def test_latest_workout():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2026-01-01", "2026-01-08", "2026-01-15"])
    })

    latest_workout = mt.calculate_latest_workout(df)

    assert latest_workout == "01/15/2026"

def test_latest_date():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2026-01-01", "2026-01-08", "2026-01-15"])
    })

    latest_date = mt.calculate_latest_date(df)

    assert latest_date == pd.Timestamp("2026-01-15")

def test_total_sessions():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2026-01-01", "2026-01-01", "2026-01-08", "2026-01-08", "2026-1-15", "2026-01-15"]),
        "set": [1, 2, 1, 2, 1, 2]
    })

    total_sessions = mt.calculate_total_sessions(df)

    assert total_sessions == 3

def test_highest_volume():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2026-01-01", "2026-01-08", "2026-01-15"]),
        "volume": [1000, 2000, 1500]
    })

    highest_volume = mt.calculate_highest_volume(df)

    assert highest_volume == 2000

def test_max_weight():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2026-01-01", "2026-01-08", "2026-01-15"]),
        "weight": [40, 35, 35]
    })

    max_weight = mt.calculate_max_weight(df)

    assert max_weight == 40

def test_most_recent_pr():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2026-01-01", "2026-01-08", "2026-01-15"]),
        "weight": [40, 35, 35]
    })

    max_weight = df.groupby("date")["weight"].max()
    max_weight_df = max_weight.reset_index() 

    total_max_weight = mt.calculate_max_weight(df)  

    most_recent_pr = mt.calculate_most_recent_pr(max_weight_df, total_max_weight)

    assert most_recent_pr == "01/01/2026"

def test_max_estimated_1rm():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2026-01-01", "2026-01-08", "2026-01-15"]),
        "estimated_1RM": [65, 89, 78]
    })

    max_estimated_1rm = mt.calculate_max_estimated_1rm(df)

    assert max_estimated_1rm == 89
