# src/preprocessor.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import json
import pandas as pd

def clean_comment_text(text):
    if not isinstance(text, str):
        return ""
    text = re.sub(r'http\S+|www\.\S+', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def preprocess_comments_pipeline():
    raw_comments_path = "data/raw/youtube_comments.csv"
    dynamic_json_path = "data/processed/dynamic_players.json"
    
    if not os.path.exists(raw_comments_path):
        print("[-] YouTube raw data missing. Run scraper first.")
        return

    if not os.path.exists(dynamic_json_path):
        print("[-] Dynamic player file absent. Run database_sync first.")
        return

    # Load active configurations dynamically
    with open(dynamic_json_path, "r") as f:
        player_dictionary = json.load(f)

    df = pd.read_csv(raw_comments_path)
    df['cleaned_text'] = df['comment_text'].apply(clean_comment_text)
    df = df[df['cleaned_text'].str.split().str.len() >= 3]
    
    targeted_rows = []
    
    print("[*] Filtering comments against your automated player database...")
    for _, row in df.iterrows():
        comment_lower = row['cleaned_text'].lower()
        title_lower = str(row['video_title']).lower() if 'video_title' in row else ""
        
        for key, meta in player_dictionary.items():
            # Check if the player's shirt name or parts of their full name match the text context
            name_parts = meta['name'].lower().split()
            if key in comment_lower or any(part in comment_lower for part in name_parts) or key in title_lower:
                new_entry = row.to_dict()
                new_entry['assigned_player'] = meta['id']
                targeted_rows.append(new_entry)
                
    processed_df = pd.DataFrame(targeted_rows)
    processed_df.to_csv("data/processed/cleaned_player_comments.csv", index=False)
    
    unique_players = len(processed_df['assigned_player'].unique()) if not processed_df.empty else 0
    print(f"[+] Text processing complete. Divided records among {unique_players} unique players.")

if __name__ == "__main__":
    preprocess_comments_pipeline()