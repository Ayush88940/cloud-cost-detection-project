import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import math
from optimizer import analyze_resources, INSTANCE_COST

# ------------------------------------------------
# PAGE CONFIG & STYLING
# ------------------------------------------------
st.set_page_config(
    page_title="Cloud Cost Control Platform",
    page_icon="☁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium CSS Injection
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        background-color: #0e1117;
    }
    
    .stMetric {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 20px;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .stMetric:hover {
        border-color: #4CAF50;
        transform: translateY(-2px);
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #4CAF50;
        color: white;
        font-weight: 600;
        border: none;
        padding: 10px;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #45a049;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
    }
    
    .header-panel {
        background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 40px;
        border-radius: 15px;
        margin-bottom: 30px;
        color: white;
    }
    
    .section-container {
        background-color: #161b22;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------
# DATA INITIALIZATION
# ------------------------------------------------
if not os.path.exists("company_usage.csv"):
    os.system("python data_generator.py")

@st.cache_data(ttl=60)
def load_data():
    return pd.read_csv("company_usage.csv")

df_raw = load_data()

# Session State Initialization
if "instances" not in st.session_state:
    st.session_state.instances = 12

if "disabled_actors" not in st.session_state:
    st.session_state.disabled_actors = {"employees": [], "teams": []}

# ------------------------------------------------
# SIDEBAR - CONTROLS
# ------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric-folders/100/cloud.png", width=80)
    st.title("Admin Console")
    st.subheader("Infrastructure Simulation")
    
    st.slider(
        "Simulation: Running Instances",
        min_value=1,
        max_value=25,
        key="instances",
        help="Simulate the current number of active server instances."
    )
    
    st.divider()
    
    if st.button("🔄 Reset Environment"):
        st.session_state.disabled_actors = {"employees": [], "teams": []}
        st.session_state.instances = 12
        st.rerun()

# ------------------------------------------------
# DATA FILTERING
# ------------------------------------------------
filtered_df = df_raw.copy()
filtered_df = filtered_df[~filtered_df["team"].isin(st.session_state.disabled_actors["teams"])]
filtered_df = filtered_df[~filtered_df["employee"].isin(st.session_state.disabled_actors["employees"])]

results = analyze_resources(filtered_df)
current_cost = st.session_state.instances * INSTANCE_COST
savings = current_cost - results["optimized_cost"]
efficiency_score = (results["required_instances"] / st.session_state.instances) * 100 if st.session_state.instances > 0 else 0

# ------------------------------------------------
# MAIN DASHBOARD UI
# ------------------------------------------------

# Header Section
st.markdown("""
<div class="header-panel">
    <h1 style='margin:0;'>Cloud Cost Control Platform</h1>
    <p style='margin:0; opacity: 0.8;'>Intelligent Infrastructure Monitoring & Optimization Dashboard</p>
</div>
""", unsafe_allow_html=True)

# Executive Summary Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Running Instances", st.session_state.instances)
with col2:
    st.metric("Required Instances", results["required_instances"], delta=int(results["required_instances"] - st.session_state.instances), delta_color="inverse")
with col3:
    st.metric("Current Monthly Cost", f"${current_cost:,}")
with col4:
    st.metric("Potential Savings", f"${savings:,}", delta=f"{efficiency_score:.1f}% Efficiency", delta_color="normal" if efficiency_score > 80 else "inverse")

st.markdown("<br>", unsafe_allow_html=True)

# Charts Section
col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("📊 Team Resource Usage vs Allocation")
    
    # Prepare data for team usage
    team_metrics = filtered_df.groupby("team").agg({
        "cpu_usage": "mean",
        "ram_usage": "mean"
    }).reset_index()
    
    fig_team = px.bar(
        team_metrics,
        x="team",
        y="cpu_usage",
        color="cpu_usage",
        color_continuous_scale="Blues",
        text_auto=".1f",
        labels={"cpu_usage": "Avg CPU %", "team": "Business Unit"}
    )
    fig_team.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        margin=dict(t=30, b=0, l=0, r=0)
    )
    st.plotly_chart(fig_team, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("💡 Optimization Impact")
    
    # Gauge for Efficiency
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = efficiency_score,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Efficiency Score"},
        gauge = {
            'axis': {'range': [0, 100]},
            'bar': {'color': "#4CAF50"},
            'steps': [
                {'range': [0, 50], 'color': "#ff4b4b"},
                {'range': [50, 80], 'color': "#ffa500"},
                {'range': [80, 100], 'color': "#4CAF50"}
            ],
        }
    ))
    fig_gauge.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        margin=dict(t=50, b=0, l=20, r=20),
        height=250
    )
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    if st.button("✨ Auto-Optimize Infrastructure"):
        st.session_state.instances = results["required_instances"]
        st.toast(f"Successfully optimized to {results['required_instances']} instances!")
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Resource Heatmap & Forecasting
col_a, col_b = st.columns(2)

with col_a:
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("🔥 Employee Workload Heatmap")
    if not filtered_df.empty:
        heatmap_data = filtered_df.pivot_table(index="employee", columns="team", values="cpu_usage")
        fig_heat = px.imshow(
            heatmap_data,
            color_continuous_scale="Viridis",
            labels=dict(x="Team", y="Employee", color="CPU %")
        )
        fig_heat.update_layout(margin=dict(t=0, b=0, l=0, r=0), paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_heat, use_container_width=True)
    else:
        st.info("No active resources to display.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_b:
    st.markdown('<div class="section-container">', unsafe_allow_html=True)
    st.subheader("📈 Cost Savings Forecast")
    
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Projection"]
    current_trend = [current_cost * (1 + (i*0.02)) for i in range(5)] + [current_cost * 1.05]
    optimized_trend = [current_cost * (1 + (i*0.02)) for i in range(5)] + [results["optimized_cost"]]
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(x=months, y=current_trend, name="Current Path", line=dict(color='#ff4b4b', dash='dash')))
    fig_trend.add_trace(go.Scatter(x=months, y=optimized_trend, name="Optimized Path", fill='tonexty', line=dict(color='#4CAF50', width=4)))
    
    fig_trend.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        margin=dict(t=30, b=0, l=0, r=0),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig_trend, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Management Panel
st.markdown('<div class="section-container">', unsafe_allow_html=True)
st.subheader("🛡️ Business Continuity & Resource Control")

tab_team, tab_emp = st.tabs(["Team Controls", "Employee Controls"])

with tab_team:
    unique_teams = df_raw["team"].unique()
    cols = st.columns(min(len(unique_teams), 4))
    for i, team in enumerate(unique_teams):
        with cols[i % 4]:
            is_active = team not in st.session_state.disabled_actors["teams"]
            status_color = "🟢 Active" if is_active else "🔴 Stopped"
            st.markdown(f"**{team}**")
            st.caption(status_color)
            if is_active:
                if st.button("Stop Units", key=f"stop_t_{team}"):
                    st.session_state.disabled_actors["teams"].append(team)
                    st.rerun()
            else:
                if st.button("Start Units", key=f"start_t_{team}"):
                    st.session_state.disabled_actors["teams"].remove(team)
                    st.rerun()

with tab_emp:
    for team in unique_teams:
        if team in st.session_state.disabled_actors["teams"]:
            continue
            
        with st.expander(f"📋 {team} Staffing"):
            team_df = df_raw[df_raw["team"] == team]
            for _, row in team_df.iterrows():
                emp = row["employee"]
                is_active = emp not in st.session_state.disabled_actors["employees"]
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"👤 {emp}")
                c2.write("✅ Active" if is_active else "❌ Idle")
                if is_active:
                    if c3.button("Suspend", key=f"susp_{emp}"):
                        st.session_state.disabled_actors["employees"].append(emp)
                        st.rerun()
                else:
                    if c3.button("Resume", key=f"res_{emp}"):
                        st.session_state.disabled_actors["employees"].remove(emp)
                        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.caption("© 2026 Cloud-Cost-Detection Project • Powered by Antigravity Intelligence")