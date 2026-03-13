import streamlit as st
import pandas as pd
import plotly.express as px
import os

from optimizer import analyze_resources

st.set_page_config(layout="wide")

st.title("Cloud Cost Control Platform")
st.caption("Business-oriented cloud infrastructure optimization")

# ------------------------------------------------
# Ensure dataset exists
# ------------------------------------------------

if not os.path.exists("company_usage.csv"):
    import data_generator
    os.system("python data_generator.py")

df = pd.read_csv("company_usage.csv")

# ------------------------------------------------
# SESSION STATE
# ------------------------------------------------

if "instances" not in st.session_state:
    st.session_state.instances = 10

if "disabled_employees" not in st.session_state:
    st.session_state.disabled_employees = []

if "disabled_teams" not in st.session_state:
    st.session_state.disabled_teams = []

# ------------------------------------------------
# FILTER ACTIVE DATA
# ------------------------------------------------

filtered_df = df[
    (~df["employee"].isin(st.session_state.disabled_employees)) &
    (~df["team"].isin(st.session_state.disabled_teams))
]

# ------------------------------------------------
# OPTIMIZER
# ------------------------------------------------

results = analyze_resources(filtered_df)

INSTANCE_COST = 5000
current_cost = st.session_state.instances * INSTANCE_COST

# ------------------------------------------------
# EXECUTIVE SUMMARY
# ------------------------------------------------

st.header("Executive Summary")

col1,col2,col3,col4,col5 = st.columns(5)

col1.metric("Current Instances", st.session_state.instances)
col2.metric("Required Instances", results["required_instances"])
col3.metric("Current Cost", f"${current_cost}")
col4.metric("Optimized Cost", f"${results['optimized_cost']}")
col5.metric("Monthly Savings", f"${current_cost-results['optimized_cost']}")

st.divider()

# ------------------------------------------------
# INFRASTRUCTURE CONTROL
# ------------------------------------------------

st.subheader("Infrastructure Control")

st.slider(
    "Adjust Running Instances",
    1,
    20,
    key="instances"
)

st.write("Active Instances:", st.session_state.instances)

# ------------------------------------------------
# TEAM RESOURCE USAGE
# ------------------------------------------------

st.subheader("Team Resource Usage")

if not filtered_df.empty:

    team_usage = filtered_df.groupby("team")["cpu_usage"].mean().reset_index()

    fig = px.bar(
        team_usage,
        x="team",
        y="cpu_usage",
        title="Average CPU Usage by Team"
    )

    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# RESOURCE HEATMAP
# ------------------------------------------------

st.subheader("Resource Heatmap")

if not filtered_df.empty:

    heatmap_df = filtered_df.pivot_table(
        index="employee",
        columns="team",
        values="cpu_usage"
    )

    fig = px.imshow(
        heatmap_df,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="Blues"
    )

    st.plotly_chart(fig, use_container_width=True)

# ------------------------------------------------
# CPU DISTRIBUTION
# ------------------------------------------------

st.subheader("CPU Usage Distribution")

if not filtered_df.empty:

    fig = px.pie(
        team_usage,
        names="team",
        values="cpu_usage"
    )

    st.plotly_chart(fig)

# ------------------------------------------------
# COST FORECAST
# ------------------------------------------------

st.subheader("Cost Forecast")

months = ["Jan","Feb","Mar","Apr","May","Jun"]

base_cost = st.session_state.instances * INSTANCE_COST

costs = [
    base_cost,
    base_cost * 0.95,
    base_cost * 0.98,
    base_cost * 1.02,
    base_cost * 0.97,
    results["optimized_cost"]
]

forecast_df = pd.DataFrame({
    "Month": months,
    "Cost": costs
})

fig = px.line(
    forecast_df,
    x="Month",
    y="Cost",
    markers=True,
    title="Infrastructure Cost Forecast"
)

st.plotly_chart(fig, use_container_width=True)

st.divider()

# ------------------------------------------------
# AUTOMATIC LEAK RESOLUTION
# ------------------------------------------------

st.subheader("Automatic Leak Resolution")

if st.button("Resolve Infrastructure Leak"):

    st.session_state.instances = results["required_instances"]

    st.success(
        f"Infrastructure optimized to {results['required_instances']} instances"
    )

    st.rerun()

# ------------------------------------------------
# EMPLOYEE CONTROL
# ------------------------------------------------

st.subheader("Employee Service Control")

for _,row in df.iterrows():

    employee = row["employee"]

    status = "ON"

    if employee in st.session_state.disabled_employees:
        status = "OFF"

    col1,col2,col3,col4,col5 = st.columns([2,2,1,1,1])

    col1.write(employee)
    col2.write(row["team"])
    col3.write(row["cpu_usage"])
    col4.write(status)

    if status == "ON":

        if col5.button("Turn Off",key=f"off_{employee}"):

            st.session_state.disabled_employees.append(employee)
            st.rerun()

    else:

        if col5.button("Turn On",key=f"on_{employee}"):

            st.session_state.disabled_employees.remove(employee)
            st.rerun()

# ------------------------------------------------
# TEAM CONTROL
# ------------------------------------------------

st.subheader("Team Control Panel")

teams = df["team"].unique()

for team in teams:

    status = "ON"

    if team in st.session_state.disabled_teams:
        status = "OFF"

    col1,col2,col3 = st.columns([3,1,1])

    col1.write(team)
    col2.write(status)

    if status == "ON":

        if col3.button("Stop Team",key=f"stop_{team}"):

            st.session_state.disabled_teams.append(team)
            st.rerun()

    else:

        if col3.button("Start Team",key=f"start_{team}"):

            st.session_state.disabled_teams.remove(team)
            st.rerun()