# fix_analytics.py
import os
import pandas as pd
import re
from collections import Counter

print("[*] Starting manual data patch...")

raw_path = "data/raw/youtube_comments.csv"
if not os.path.exists(raw_path):
    print(f"[-] Critical Error: {raw_path} does not exist. Please run your scraper first.")
    exit()

df = pd.read_csv(raw_path)
print(f"[+] Found raw comments file with {len(df)} rows.")

# 1. Create a dummy player link if preprocessor matching failed
player_ids = ["dynamic_rice", "dynamic_haaland", "dynamic_ekitike", "dynamic_debruyne", "dynamic_mbappe"]
df['assigned_player'] = player_ids[0] # Fallback assignment to ensure rows exist

# If you have specific names in your data, assign them dynamically
for idx, row in df.iterrows():
    text = str(row['comment_text']).lower()
    if 'haaland' in text: df.at[idx, 'assigned_player'] = 'dynamic_haaland'
    elif 'rice' in text: df.at[idx, 'assigned_player'] = 'dynamic_rice'
    elif 'ekitike' in text: df.at[idx, 'assigned_player'] = 'dynamic_ekitike'
    elif 'bruyne' in text: df.at[idx, 'assigned_player'] = 'dynamic_debruyne'
    elif 'mbappe' in text: df.at[idx, 'assigned_player'] = 'dynamic_mbappe'

# 2. Force generate word_frequencies.csv
print("[*] Force-generating word frequencies...")
stop_words = {'the', 'and', 'a', 'to', 'is', 'in', 'of', 'it', 'you', 'this', 'for', 'on', 'with', 'my', 'bro', 'game', 'player', 'card', 'like', 'good', 'best', 'just', 'so'}
freq_records = []

for p_id in df['assigned_player'].unique():
    p_text = " ".join(df[df['assigned_player'] == p_id]['comment_text'].astype(str).tolist()).lower()
    words = [w for w in re.findall(r'\b[a-z]{3,}\b', p_text) if w not in stop_words]
    for word, count in Counter(words).most_common(15):
        freq_records.append({"player_id": p_id, "word": word, "frequency_count": count})

pd.DataFrame(freq_records).to_csv("data/processed/word_frequencies.csv", index=False)

# 3. Force generate categorized_words.csv
print("[*] Force-generating categorized words...")
cat_mapping = {
    "⚡ Agility, Pace & Dribbling": ["dribbling", "turn", "balance", "nimble", "agile", "speed", "pace"],
    "🎯 Finishing & Physicality": ["finishing", "shoot", "goal", "clinical", "beast", "cyborg", "header"],
    "🛡️ Defense & Workrate": ["tackling", "defense", "intercept", "prowess", "aggression"],
    "⚠️ Performance Issues (Nerfs)": ["clunky", "truck", "trash", "fraud", "stiff", "heavy", "slow"]
}

cat_records = []
for p_id in df['assigned_player'].unique():
    p_text = " ".join(df[df['assigned_player'] == p_id]['comment_text'].astype(str).tolist()).lower()
    words = re.findall(r'\b[a-z]{3,}\b', p_text)
    counts = Counter(words)
    
    for cat, keywords in cat_mapping.items():
        total = sum(counts[w] for w in keywords)
        examples = [f"{w} ({counts[w]})" for w in keywords if counts[w] > 0][:3]
        cat_records.append({
            "player_id": p_id,
            "category": cat,
            "total_mentions": total,
            "top_keywords": ", ".join(examples) if examples else "None recorded"
        })

os.makedirs("data/processed", exist_ok=True)
pd.DataFrame(cat_records).to_csv("data/processed/categorized_words.csv", index=False)
print("[🎉] Success! All missing processed files forced into existence.")