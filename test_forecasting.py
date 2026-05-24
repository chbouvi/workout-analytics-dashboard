import pandas as pd
from forecasting import calculate_weight_forecast

def test_forecast_two_increasing_workouts():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2026-01-01", "2026-01-08"]),
        "weight": [100, 110]
    })

    predicted_weight, slope, result_df = calculate_weight_forecast(df)

    assert slope == 10
    assert predicted_weight == 120

def test_forecast_one_workout():
    df = pd.DataFrame({
        "date": pd.to_datetime(["2026-01-01"]),
        "weight": [100]
    })

    predicted_weight, slope, result_df = calculate_weight_forecast(df)

    assert slope is None
    assert predicted_weight is None