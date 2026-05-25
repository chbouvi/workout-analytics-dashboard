import pandas as pd
import streamlit as st 
import plotly.express as px 
from google import genai
from forecasting import calculate_weight_forecast

# Load workout data
df = pd.read_csv("workouts.csv")

exercises_array = df["exercise"].unique()
exercises_list = exercises_array.tolist()
exercises_list.append("Other...")

# Cleaner date
df["date"] = pd.to_datetime(df["date"])

# Calculate volume per row (and then each set be added together)
df["volume"] = df["weight"] * df["reps"]

# Calculate 1RM per row
df["estimated_1RM"] = df["weight"] * (1 + df["reps"]/30)

st.title("Workout Progress Dashboard", anchor=False)

# Show data
#st.write(df)

#Filter exercise

st.sidebar.header("Exercise Filter")

exercise = st.sidebar.selectbox(
    "Choose Exercise",
    df["exercise"].unique()
)

st.sidebar.divider()

st.sidebar.header("Workout Form")

select_date = st.sidebar.date_input(
    "Date: "
)

select_date = pd.to_datetime(select_date)

select_exercise = st.sidebar.selectbox(
    "New Exercise ",
    exercises_list
)

if select_exercise == "Other...":
    select_exercise = st.sidebar.text_input(
        "Enter Exercise Name: "
    )

select_exercise = select_exercise.strip()

select_set = st.sidebar.number_input(
    "Set: ",
    value=1,
    step=1,
    min_value=1
)

select_weight = st.sidebar.number_input(
    "Weight: ",
    value=1,
    step=1,
    min_value=1
)

select_reps = st.sidebar.number_input(
    "Reps: ",
    value=1,
    step=1,
    min_value=1
)

select_notes = st.sidebar.text_input(
    "Notes: ",
)

if st.sidebar.button("Add Set"):
    if select_exercise == "":
        st.sidebar.error("Please enter an exercise")
    else:
        new_set = {
            "date": [select_date],
            "exercise": [select_exercise],
            "set": [select_set],
            "weight": [select_weight],
            "reps": [select_reps],
            "notes": [select_notes]
        }
        new_df = pd.DataFrame(new_set)

        updated_df = pd.concat([df, new_df], ignore_index=True)

        raw_columns = ["date", "exercise", "set", "weight", "reps", "notes"]
        updated_df = updated_df[raw_columns]

        updated_df.to_csv("workouts.csv", index=False)
        st.sidebar.success("Set added successfully")
        st.rerun()

exercise_df = df[df["exercise"] == exercise]

latest_workout = exercise_df["date"].max().strftime("%m/%d/%y")
latest_date = exercise_df["date"].max()

# Calculate total sessions for this exercise
sessions_df = exercise_df.groupby("date")["set"].max()
total_sessions = len(sessions_df)

volume = exercise_df.groupby("date")["volume"].sum()
volume_df = volume.reset_index()
highest_volume = int(volume_df["volume"].max())
#highest_volume = volume_df.groupby("date")["volume"].sum().max()

#st.write(volume_df)

max_weight = exercise_df.groupby("date")["weight"].max()
max_weight_df = max_weight.reset_index()
total_max_weight = int(max_weight_df["weight"].max())

predicted_weight, m, max_weight_df = calculate_weight_forecast(max_weight_df)

pr_rows_df = max_weight_df[max_weight_df["weight"] == total_max_weight]
most_recent_pr = pr_rows_df["date"].max()
most_recent_pr = most_recent_pr.strftime("%m/%d/%y")

max_1RM = exercise_df.groupby("date")["estimated_1RM"].max()
max_1RM_df = max_1RM.reset_index()
total_max_1RM = int(max_1RM_df["estimated_1RM"].max())

# Create graph

fig1 = px.line(
    max_weight_df,
    x="date",
    y="weight",
    title=f"{exercise} Progress",
    markers=True
)

fig1.update_layout(
    xaxis_title="Date",
    yaxis_title="Max Weight (lbs)"
)

workout_dates = max_weight_df["date"].sort_values()
date_gaps = workout_dates.diff().dropna()
if len(date_gaps) == 0:
    usual_gap = pd.Timedelta(days=7)
else:
    usual_gap = date_gaps.median()
next_date = latest_date + usual_gap

if predicted_weight is not None:
    fig1.add_scatter(
        x = max_weight_df["date"],
        y = max_weight_df["predicted_weight"],
        mode = "lines",
        name = "Trendline"
    )
    fig1.add_scatter(
        x = [next_date],
        y = [predicted_weight],
        mode = "markers",
        name = "Prediction Point"
    )

fig2 = px.bar(
    volume_df,
    x="date",
    y="volume",
    title="Volume Progress"
)

fig2.update_layout(
    xaxis_title="Date",
    yaxis_title="Volume"
)

fig3 = px.line(
    max_1RM_df,
    x="date",
    y="estimated_1RM",
    title="1RM Progress",
    markers=True
)

fig3.update_layout(
    xaxis_title="Date",
    yaxis_title="Estimated 1RM"
)

st.subheader("Performance Metrics")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Sessions", total_sessions)

with col2:
    st.metric("Max Weight", total_max_weight)

with col3:
    st.metric("PR Date", most_recent_pr)

col4, col5, col6 = st.columns(3)  

with col4:
    st.metric("Highest Volume", highest_volume)

with col5:
    st.metric("Estimated 1RM", total_max_1RM)

with col6:
    st.metric("Latest Workout", latest_workout)

st.subheader("Prediction")

if predicted_weight is None:
    st.metric("Predicted Next Weight", "N/A")
else:
    st.metric("Predicted Next Weight", round(predicted_weight, 1))

st.divider()

st.subheader("Progress Charts")

st.plotly_chart(fig1, width="stretch")
st.plotly_chart(fig2, width="stretch")
st.plotly_chart(fig3, width="stretch")

st.subheader("AI Workout Insights")

api_key = st.secrets["Gemini_Key"]
client = genai.Client(api_key=api_key)

insight_prompt = f"""
    Exercise: {exercise}
    Sessions: {total_sessions}
    Max Weight: {total_max_weight}
    Estimated 1RM: {total_max_1RM}
    Predicted Next Weight: {predicted_weight}
    Latest Workout: {latest_workout}
    Highest Volume: {highest_volume}
    Most Recent PR Date: {most_recent_pr}
    Regression Slope: {m}

    Give:
    1. Progress assessment
    2. Strengths
    3. Suggestions
    4. Predicted future progress
"""

if st.button("Generate AI Insights"):
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=insight_prompt
    )
    st.markdown(response.text)

st.divider()

st.subheader("Workout History")
st.dataframe(exercise_df)