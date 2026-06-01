# app/text_analytics_app.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
import pandas as pd
from src.text_orchestrator import execute_text_only_pipeline

st.set_page_config(
    page_title="eFootball Community Voice Analytics", 
    page_icon="🗣️", 
    layout="wide"
)

# --- SIDEBAR: TEXT RUNTIME CONTROLLER ---
st.sidebar.title("🛠️ Text Processing Hub")
st.sidebar.markdown(
    "Use this control switch to parse, clean, and re-sort your local "
    "`youtube_comments.csv` file without initiating external web API calls."
)

if st.sidebar.button("⚙️ Re-Run Word Categorization Engine"):
    log_box = st.sidebar.empty()
    text_progress = st.sidebar.progress(0.0)
    
    stream_logs = ""
    pipeline_runner = execute_text_only_pipeline()
    
    for idx, log_update in enumerate(pipeline_runner):
        stream_logs += log_update + "\n"
        log_box.text_area("Engine Runtime Logs:", stream_logs, height=180)
        
        if "✅" in log_update:
            # 3 steps = 33.3% progress increments per success tick
            text_progress.progress(min((idx + 1) * 0.33, 1.0))
            
    st.sidebar.success("Analytics Updated! Refreshing charts...")
    st.rerun()

st.sidebar.markdown("---")

# --- MAIN DASHBOARD INTERFACE ---
st.title("🗣️ eFootball Community Voice Dashboard")
st.subheader("Deep Categorization & Text Taxonomy Explorer")

CATEGORIZED_DATA_PATH = "data/processed/categorized_words.csv"
FREQUENCY_DATA_PATH = "data/processed/word_frequencies.csv"
EFHUB_STATS_PATH = "data/processed/efhub_stats.csv"

# Guide user if they open the application for the first time without processing files
if not os.path.exists(CATEGORIZED_DATA_PATH) or not os.path.exists(FREQUENCY_DATA_PATH):
    st.warning("⚠️ Local analytics files not found. Please click 'Re-Run Word Categorization Engine' in the sidebar to process your raw datasets.")
    st.stop()

df_cat = pd.read_csv(CATEGORIZED_DATA_PATH)
df_freq = pd.read_csv(FREQUENCY_DATA_PATH)
df_players = pd.read_csv(EFHUB_STATS_PATH)

selected_player_id = st.selectbox(
    "Select Player to Inspect Feedback:", 
    df_cat['player_id'].unique(),
    format_func=lambda x: str(x).replace("dynamic_", "").upper()
)

player_cat_df = df_cat[df_cat['player_id'] == selected_player_id]
player_freq_df = df_freq[df_freq['player_id'] == selected_player_id]

try:
    player_label = df_players[df_players['player_id'] == selected_player_id]['display_name'].iloc[0]
except IndexError:
    player_label = str(selected_player_id).replace("dynamic_", "").capitalize()

st.markdown(f"## Active Card Profile: **{player_label}**")
st.markdown("---")

col_left, col_right = st.columns([3, 2], gap="large")

with col_left:
    st.write("### 🗂️ Categorized Community Breakdown")
    st.markdown("How frequently specific gameplay dimensions are mentioned by users:")
    
    total_mentions_all_categories = player_cat_df['total_mentions'].sum()
    
    for _, row in player_cat_df.iterrows():
        cat_name = row['category']
        mentions = row['total_mentions']
        top_words = row['top_keywords']
        
        percentage = (mentions / total_mentions_all_categories) if total_mentions_all_categories > 0 else 0.0
        
        with st.container(border=True):
            metric_col, progress_col = st.columns([1, 2])
            with metric_col:
                st.metric(label=cat_name, value=f"{mentions} mentions")
            with progress_col:
                st.write(f"**Share of Discussion:** {percentage:.1%}")
                st.progress(percentage)
                st.caption(f"**Dominant phrases:** *{top_words}*")

with col_right:
    st.write("### 🏆 Top 15 Individual Buzzwords")
    st.markdown("Raw frequency leaderboard of terms across the comment dataset:")
    
    if not player_freq_df.empty:
        display_freq_df = player_freq_df[["word", "frequency_count"]].reset_index(drop=True)
        display_freq_df.columns = ["Community Term", "Total Appearances"]
        
        st.dataframe(
            display_freq_df,
            use_container_width=True,
            hide_index=False,
            height=510
        )
        top_term = display_freq_df.iloc[0]["Community Term"]
        st.success(f"💡 **NLP Takeaway:** The word '**{top_term}**' is dominating community discussion for this card.")
    else:
        st.info("No buzzword stats computed for this asset yet.")