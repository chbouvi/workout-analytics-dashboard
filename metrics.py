def calculate_latest_workout(exercise_df):
    return exercise_df["date"].max().strftime("%m/%d/%y")

def calculate_latest_date(exercise_df):
    return exercise_df["date"].max()

def calculate_total_sessions(exercise_df):
    sessions_df = exercise_df.groupby("date")["set"].max()
    return len(sessions_df)

def calculate_highest_volume(exercise_df):
    volume = exercise_df.groupby("date")["volume"].sum()
    volume_df = volume.reset_index()
    return int(volume_df["volume"].max())

def calculate_max_weight(exercise_df):
    max_weight = exercise_df.groupby("date")["weight"].max()
    max_weight_df = max_weight.reset_index()
    return int(max_weight_df["weight"].max())

def calculate_most_recent_pr(max_weight_df, total_max_weight):
    pr_rows_df = max_weight_df[max_weight_df["weight"] == total_max_weight]
    return pr_rows_df["date"].max().strftime("%m/%d/%y")

def calculate_max_estimated_1rm(exercise_df):
    max_1rm = exercise_df.groupby("date")["estimated_1RM"].max()
    max_1rm_df = max_1rm.reset_index()
    return int(max_1rm_df["estimated_1RM"].max())