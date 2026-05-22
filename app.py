import pandas as pd
import streamlit as st 
import plotly.express as px 

# Load workout data
df = pd.read_csv("workouts.csv")

exercises_array = df["exercise"].unique()
exercises_list = exercises_array.tolist()
exercises_list.append("Other...")

# Cleaner date
df["date"] = pd.to_datetime(df["date"])

# Calculate volume per row (and then each set be added together)
df["volume"] = df["weight"] * df["reps"]

st.title("Workout Progress Dashboard", anchor=False)

# Show data
#st.write(df)

#Filter exercise

st.sidebar.header("Exercise Filter")

exercise = st.sidebar.selectbox(
    "Choose Exercise",
    df["exercise"].unique()
)

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

if st.sidebar.button("Add Set"):
    if select_exercise == "":
        st.error("Please enter an exercise")
    else:
        new_volume = select_weight * select_reps
        new_set = {
            "date": [select_date],
            "exercise": [select_exercise],
            "set": [select_set],
            "weight": [select_weight],
            "reps": [select_reps],
            "volume": [new_volume]
        }
        new_df = pd.DataFrame(new_set)
        updated_df = pd.concat([df, new_df], ignore_index=True)
        updated_df.to_csv("workouts.csv", index=False)
        st.sidebar.success("Set added successfully")
        st.rerun()

exercise_df = df[df["exercise"] == exercise]

# Calculate total sessions for this exercise
sessions_df = exercise_df.groupby("date")["set"].max()
total_sessions = len(sessions_df)

volume_df = exercise_df.groupby("date")["volume"].sum()
volume_df = volume_df.reset_index()
highest_volume = volume_df["volume"].max()
#highest_volume = volume_df.groupby("date")["volume"].sum().max()

#st.write(volume_df)

max_weight = exercise_df.groupby("date")["weight"].max()
max_weight_df = max_weight.reset_index()
total_max_weight = max_weight_df["weight"].max()

pr_rows_df = max_weight_df[max_weight_df["weight"] == total_max_weight]
most_recent_pr = pr_rows_df["date"].max()
most_recent_pr = most_recent_pr.strftime("%m/%d/%y")

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

st.subheader("Performance Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Sessions", total_sessions)

with col2:
    st.metric("Max Weight", total_max_weight)

with col3:
    st.metric("PR Date", most_recent_pr)

with col4:
    st.metric("Highest Volume", highest_volume)

st.divider()

st.subheader("Progress Charts")

st.plotly_chart(fig1)
st.plotly_chart(fig2)
