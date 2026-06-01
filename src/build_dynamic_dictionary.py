# src/build_dynamic_dictionary.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import json
import pandas as pd

def extract_position_from_context(text_lower):
    """Detects a player's field position based on video title keywords."""
    midfield_tokens = ["cmf", "dmf", "amf", "midfielder", "box-to-box", "orchestrator", "anchor man"]
    forward_tokens = ["striker", "cf", "rwf", "lwf", "poacher", "goal poacher", "winger", "finishing"]
    defense_tokens = ["cb", "lb", "rb", "defender", "build up", "destroyer", "goalkeeper", "gk"]
    
    if any(token in text_lower for token in midfield_tokens):
        return "MID"
    if any(token in text_lower for token in forward_tokens):
        return "FWD"
    if any(token in text_lower for token in defense_tokens):
        return "DEF"
    return "MID" # Default middle-ground baseline stat profile

def generate_dynamic_dictionary():
    raw_csv_path = "data/raw/youtube_comments.csv"
    if not os.path.exists(raw_csv_path):
        print("[-] YouTube raw data missing. Please run src/scraper.py first.")
        return
        
    df = pd.read_csv(raw_csv_path)
    if 'video_title' not in df.columns:
        print("[-] Error: Scraped data layout lacks video tracking titles.")
        return
        
    unique_titles = df['video_title'].dropna().unique()
    dynamic_registry = {}
    
    # Common video title noise words to ignore when extracting player names
    stop_words = {"one", "the", "best", "of", "review", "is", "player", "players", "pack", "opening", "in"}

    print(f"[*] Parsing {len(unique_titles)} distinct content titles for entities...")

    for title in unique_titles:
        title_clean = re.sub(r'[^a-zA-Z\s\-]', '', title) # Clear emojis, numbers, brackets
        words = title_clean.split()
        title_lower = title.lower()
        
        # Strategy: Look for capitalized string sequences (e.g. "DECLAN RICE" or "HAALAND")
        for word in words:
            if word.isupper() and len(word) > 2 and word.lower() not in stop_words:
                player_key = word.lower()
                player_id = f"dynamic_{player_key}"
                
                if player_key not in dynamic_registry:
                    detected_pos = extract_position_from_context(title_lower)
                    
                    dynamic_registry[player_key] = {
                        "id": player_id,
                        "name": word.capitalize(),
                        "pos": detected_pos
                    }
                    
    # Export down to systemic storage locations
    output_dir = os.path.join("data", "processed")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, "dynamic_players.json")
    with open(output_path, "w") as f:
        json.dump(dynamic_registry, f, indent=4)
        
    print(f"[+] Dynamic dictionary built successfully! Registered {len(dynamic_registry)} players at: {output_path}")

if __name__ == "__main__":
    generate_dynamic_dictionary()