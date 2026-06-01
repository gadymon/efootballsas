# src/database_sync.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import json

def get_efhub_mock_database():
    os.makedirs("data/processed", exist_ok=True)
    
    master_db_path = "data/raw/efootball_master_db.csv"
    dynamic_json_path = "data/processed/dynamic_players.json"

    if not os.path.exists(master_db_path):
        print(f"[-] Error: Please drop your dataset into {master_db_path} first.")
        return pd.DataFrame()

    # Load your raw dataset
    master_df = pd.read_csv(master_db_path)
    
    # Filter: Skip Goalkeepers (GK) since they don't use outfield stats
    master_df = master_df[master_df['position'] != 'GK']
    
    matched_players_data = []
    registered_dynamic_profiles = {}

    print(f"[*] Processing {len(master_df)} outfield players from your dataset...")

    for _, row in master_df.iterrows():
        # Create a standardized key for text matching (e.g., "K. De Bruyne" -> "de bruyne")
        full_name = str(row['player_name'])
        shirt_name = str(row['shirt_name']).lower()
        
        # Unique systemic ID
        player_id = f"dynamic_{shirt_name}"
        display_label = f"{full_name} ({row['club_name']})"
        
        # Map your exact file columns to the dashboard structure
        matched_players_data.append({
            "player_id": player_id,
            "display_name": display_label,
            "dribbling": int(row['ball_control']),       # Using ball_control as core agility metric
            "defending": int(row['defensive_prowess']), # Map directly to your file column
            "passing": int(row['low_pass']),             # Map directly to your file column
            "shooting": int(row['finishing'])           # Map directly to your file column
        })
        
        # Re-build the tracking rules dictionary for the preprocessor engine
        registered_dynamic_profiles[shirt_name] = {
            "id": player_id,
            "name": full_name,
            "pos": str(row['position'])
        }

    # Save out the unified stats matrix for the UI
    df_output = pd.DataFrame(matched_players_data)
    df_output.to_csv("data/processed/efhub_stats.csv", index=False)
    
    # Write the dictionary out so other files stay perfectly synced
    with open(dynamic_json_path, "w") as f:
        json.dump(registered_dynamic_profiles, f, indent=4)
        
    print(f"[+] Output synchronized! Formatted {len(df_output)} profiles inside data/processed/efhub_stats.csv")
    return df_output

if __name__ == "__main__":
    get_efhub_mock_database()