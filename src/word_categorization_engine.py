# src/word_categorization_engine.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import re
from collections import Counter

def categorize_community_words():
    cleaned_comments_path = "data/processed/cleaned_player_comments.csv"
    output_category_path = "data/processed/categorized_words.csv"
    
    if not os.path.exists(cleaned_comments_path):
        print("[-] Cleaned player comments file missing. Please run preprocessing first.")
        return

    df = pd.read_csv(cleaned_comments_path)
    
    # Define our categorizations mapping matrix
    CATEGORY_MAPPING = {
        "⚡ Agility, Pace & Dribbling": ["dribbling", "turn", "balance", "nimble", "agile", "speed", "pace", "smooth", "fast", "run"],
        "🎯 Finishing & Physicality": ["finishing", "shoot", "goal", "clinical", "beast", "cyborg", "header", "heading", "strength", "physical"],
        "🛡️ Defense & Workrate": ["tackling", "defense", "intercept", "prowess", "aggression", "reach", "track", "workrate", "solid"],
        "⚠️ Performance Issues (Nerfs)": ["clunky", "truck", "trash", "fraud", "stiff", "heavy", "slow", "ghost", "nerfed", "clunky"]
    }

    categorized_records = []

    # Process each player found in the pipeline
    for player_id in df['assigned_player'].unique():
        player_df = df[df['assigned_player'] == player_id]
        
        # Merge comments to tokenize
        all_text = " ".join(player_df['cleaned_text'].astype(str).tolist()).lower()
        words = re.findall(r'\b[a-z]{3,}\b', all_text)
        
        # Count words for this specific player
        word_counts = Counter(words)
        
        # Track counts per category
        category_sums = {cat: 0 for cat in CATEGORY_MAPPING.keys()}
        category_examples = {cat: [] for cat in CATEGORY_MAPPING.keys()}
        
        for word, count in word_counts.items():
            for category, keywords in CATEGORY_MAPPING.items():
                if word in keywords:
                    category_sums[category] += count
                    category_examples[category].append(f"{word} ({count})")
                    
        # Structure the dataset row entries
        for category in CATEGORY_MAPPING.keys():
            # Get the top 3 most frequent words as examples for context
            examples_sorted = sorted(category_examples[category], key=lambda x: int(re.search(r'\((\d+)\)', x).group(1)), reverse=True)[:3]
            examples_str = ", ".join(examples_sorted) if examples_sorted else "None recorded"
            
            categorized_records.append({
                "player_id": player_id,
                "category": category,
                "total_mentions": category_sums[category],
                "top_keywords": examples_str
            })

    output_df = pd.DataFrame(categorized_records)
    os.makedirs("data/processed", exist_ok=True)
    output_df.to_csv(output_category_path, index=False)
    print(f"[+] Categorization catalog exported successfully to: {output_category_path}")
    return output_df

if __name__ == "__main__":
    categorize_community_words()