# app/dashboard.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
import json
from src.orchestrator import execute_full_pipeline

st.set_page_config(page_title="eFootball Sentiment Analytics", layout="wide")

# --- SIDEBAR: PIPELINE CONTROLLER & AUTOMATION ---
st.sidebar.title("⚙️ Automation Control Center")
st.sidebar.markdown("Use this panel to fetch raw YouTube comment feeds and re-calculate the Sentiment Adjusted Stats dynamically.")

# Input for updating configuration at runtime
api_key_input = st.sidebar.text_input("YouTube API Key:", type="password", help="Enter your Google Cloud Console API Key")
if api_key_input:
    os.environ["YOUTUBE_API_KEY"] = api_key_input

st.sidebar.markdown("---")
st.sidebar.subheader("Execute Pipeline Routine")

if st.sidebar.button("🚀 Run Full Automated Scrape & ML Pipeline"):
    log_container = st.sidebar.empty()
    progress_bar = st.sidebar.progress(0.0)
    
    # Run pipeline generator and display status logs live
    log_text = ""
    status_generator = execute_full_pipeline()
    
    for idx, status in enumerate(status_generator):
        log_text += status + "\n"
        log_container.text_area("Pipeline Progress Logs:", log_text, height=200)
        # 5 distinct steps = 20% progress increment per success step message
        if "✅" in status:
            progress_bar.progress(min((idx + 1) * 0.1, 1.0))
            
    st.sidebar.success("Process Complete! Refreshing charts...")
    st.rerun()

# --- MAIN DASHBOARD: VISUALIZATION ---
st.title("⚽ eFootball Analytics Engine")
st.subheader("Community Sentiment-Adjusted Stats vs. Base EFHub Data")

try:
    df = pd.read_csv("data/processed/calculated_sas_matrix.csv")
    dynamic_dict_path = "data/processed/dynamic_players.json"
    
    if os.path.exists(dynamic_dict_path):
        with open(dynamic_dict_path, "r") as f:
            registry = json.load(f)
            st.sidebar.metric("Total Tracked Players", len(registry))
except FileNotFoundError:
    st.warning("⚠️ Welcome! No parsed data detected yet. Please provide your YouTube API Key in the sidebar and click 'Run Full Automated Scrape & ML Pipeline' to populate your analytics server.")
    st.stop()

# Dropdown picker for selecting card profiles found dynamically
selected_name = st.selectbox("Select Target Card Profile:", df['display_name'].unique())
player_row = df[df['display_name'] == selected_name].iloc[0]

# Organize data layout for visualization
categories = ["Dribbling/Agility", "Defending", "Passing Quality", "Shooting/Finishing"]
base_metrics = [player_row['dribbling_base'], player_row['defending_base'], player_row['passing_base'], player_row['shooting_base']]
sas_metrics = [player_row['dribbling_sas'], player_row['defending_sas'], player_row['passing_sas'], player_row['shooting_sas']]

chart_data = pd.DataFrame({
    "Attribute Category": categories,
    "EFHub Baseline": base_metrics,
    "Sentiment Adjusted Stat (SAS)": sas_metrics
}).set_index("Attribute Category")

col1, col2 = st.columns([1, 2])

with col1:
    st.metric(label="Calculated Profile ID", value=player_row['player_id'].upper())
    st.markdown("---")
    
    # Generate interactive delta metrics
    for cat, base, sas in zip(categories, base_metrics, sas_metrics):
        diff = sas - base
        st.metric(label=cat, value=f"SAS: {sas} (Base: {base})", delta=diff)

with col2:
    st.write("### Statistical Deviation Visualizer")
    st.bar_chart(chart_data, height=420)
    
    st.info("💡 Insight: When SAS exceeds the baseline, the community finds the card performing better than its raw database stats (hidden player ID advantage). A negative deviation warns that the card plays clunkier than advertised.")