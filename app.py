import pandas as pd
import streamlit as st 
import plotly.express as px 
from google import genai
from forecasting import calculate_weight_forecast
import metrics as mt

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
    "Select Exercise",
    df["exercise"].unique()
)

st.sidebar.divider()

st.sidebar.header("Log Workout")

select_date = st.sidebar.date_input(
        "Date: "
    )

select_date = pd.to_datetime(select_date)

select_exercise = st.sidebar.selectbox(
    "Exercise ",
    exercises_list
)

if select_exercise == "Other...":
    custom_exercise = st.sidebar.text_input(
        "Enter Exercise Name: "
    )
    final_exercise = custom_exercise.strip()

else: 
    final_exercise = select_exercise.strip()

select_sets = st.sidebar.number_input(
    "Number of Sets: ",
    value=1,
    step=1,
    min_value=1
)

with st.sidebar.form("workout_form", clear_on_submit=True):

    set_rows = []

    for i in range(select_sets):
        set_number = i + 1
        select_weight = st.number_input(
            f"Set {set_number} Weight: ",
            value=1,
            step=1,
            min_value=1
        )

        select_reps = st.number_input(
            f"Set {set_number} Reps: ",
            value=1,
            step=1,
            min_value=1
        )

        select_notes = st.text_input(
            f"Set {set_number} Notes: ",
        )
        set_rows.append({
            "date": select_date,
            "exercise": final_exercise,
            "set": set_number, 
            "weight": select_weight, 
            "reps": select_reps, 
            "notes": select_notes
        })
    
    submitted = st.form_submit_button("Add Exercise")

if submitted:
    if final_exercise == "":
        st.error("Please enter an exercise")
    else:
        new_df = pd.DataFrame(set_rows)
        updated_df = pd.concat([df, new_df], ignore_index=True)

        raw_columns = ["date", "exercise", "set", "weight", "reps", "notes"]
        updated_df = updated_df[raw_columns]

        updated_df.to_csv("workouts.csv", index=False)
        st.success("Exercise added successfully")
        st.rerun()

exercise_df = df[df["exercise"] == exercise]

notes_by_date = []

for date, rows in exercise_df.groupby("date"):
    notes = rows["notes"].dropna()
    notes = notes[notes != ""]

    if len(notes) > 0:
        notes_text = "; ".join(notes)
        notes_by_date.append(f"{date}: {notes_text}")

notes_summary = "\n".join(notes_by_date)
if notes_summary == "":
    notes_summary = "No notes recorded."

latest_workout = mt.calculate_latest_workout(exercise_df)
latest_date = mt.calculate_latest_date(exercise_df)

# Calculate total sessions for this exercise
total_sessions = mt.calculate_total_sessions(exercise_df)

# Calculate highest volume for this exercise
highest_volume = mt.calculate_highest_volume(exercise_df)

max_weight = exercise_df.groupby("date")["weight"].max()
max_weight_df = max_weight.reset_index()

volume = exercise_df.groupby("date")["volume"].sum()
volume_df = volume.reset_index()

max_1rm = exercise_df.groupby("date")["estimated_1RM"].max()
max_1rm_df = max_1rm.reset_index()

# Calculate max 1RM
total_max_1rm = mt.calculate_max_estimated_1rm(exercise_df)

total_max_weight = mt.calculate_max_weight(exercise_df)

max_weight_df["moving_average"] = max_weight_df["weight"].rolling(window=3, min_periods=1).mean()

predicted_weight, m, max_weight_df = calculate_weight_forecast(max_weight_df)

# Calculate most recent PR
most_recent_pr = mt.calculate_most_recent_pr(max_weight_df, total_max_weight)


# Create charts

fig1 = px.line(
    max_weight_df,
    x="date",
    y="weight",
    title=f"{exercise} Progress",
    markers=True
)

fig1.data[0].name = "Max Weight"
fig1.data[0].showlegend = True

fig1.update_layout(
    xaxis_title="Date",
    yaxis_title="Max Weight (lbs)"
)

fig1.add_scatter(
    x = max_weight_df["date"],
    y = max_weight_df["moving_average"],
    mode = "lines",
    name = "3-Workout Moving Average",
    line=dict(dash="dot")
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
    max_1rm_df,
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
    st.metric("Estimated 1RM", total_max_1rm)

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
    Estimated 1RM: {total_max_1rm}
    Predicted Next Weight: {predicted_weight}
    Latest Workout: {latest_workout}
    Highest Volume: {highest_volume}
    Most Recent PR Date: {most_recent_pr}
    Regression Slope: {m}
    Workout Notes: {notes_summary}

    Give:
    1. Progress assessment
    2. Strengths
    3. Suggestions
    4. Predicted future progress
"""

if st.button("Generate AI Insights"):
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=insight_prompt
        )
        st.markdown(response.text)
    except Exception as e:
        st.error("AI insights are temporarily unavailable. Please try again later.")

st.divider()

history_columns = [
    "date",
    "exercise",
    "set",
    "weight",
    "reps",
    "volume",
    "estimated_1RM",
    "notes"
]

history_df = exercise_df[history_columns]

st.subheader("Workout History")
st.dataframe(history_df)