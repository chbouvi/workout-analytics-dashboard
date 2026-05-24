def calculate_weight_forecast(max_weight_df):
    if len(max_weight_df) < 2:
        return None, None, max_weight_df

    max_weight_df = max_weight_df.copy()
    max_weight_df["workout_num"] = range(len(max_weight_df))

    x = max_weight_df["workout_num"]
    y = max_weight_df["weight"]

    x_mean = x.mean()
    y_mean = y.mean()

    numerator = ((x - x_mean)*(y - y_mean)).sum()
    denominator = ((x - x_mean) ** 2).sum()

    m = numerator / denominator
    b = y_mean - m * x_mean

    predicted_weight = m * len(max_weight_df)
    predicted_weight += b

    max_weight_df["predicted_weight"] = m * max_weight_df["workout_num"] + b

    return predicted_weight, m, max_weight_df