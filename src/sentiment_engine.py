import sys
import os
# Adds the root directory (one level up from 'src') to the Python path list
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from transformers import pipeline
from config.settings import (
    MODEL_NAME, MAX_TOKEN_LENGTH, GAMING_SLANG_DICTIONARY, 
    STAT_ATTRIBUTE_MAPPING, MAX_STAT_ADJUSTMENT, BASE_ADJUSTMENT_MULTIPLIER
)

class eFootballSentimentEngine:
    def __init__(self):
        print("[*] Warming up HuggingFace Sequence Classification Pipeline...")
        self.classifier = pipeline(
            "sentiment-analysis", 
            model=MODEL_NAME, 
            tokenizer=MODEL_NAME,
            device=-1 # Set to 0 if running locally with an active CUDA GPU environment
        )
        
    def score_text_sentiment(self, text):
        lower_text = text.lower()
        try:
            inference = self.classifier(text[:MAX_TOKEN_LENGTH])[0]
            label = inference['label']
            base_score = inference['score']
        except Exception:
            return 0.0

        score = base_score if label == 'positive' else (-base_score if label == 'negative' else 0.0)
        
        # Apply community slang corrections
        for boost in GAMING_SLANG_DICTIONARY["positive_boosts"]:
            if boost in lower_text and score <= 0.2:
                score += 0.4
        for nerf in GAMING_SLANG_DICTIONARY["negative_nerfs"]:
            if nerf in lower_text and score >= -0.2:
                score -= 0.4
                
        return float(np.clip(score, -1.0, 1.0))

    def compute_sentiment_adjusted_stats(self):
        try:
            comments_df = pd.read_csv("data/processed/cleaned_player_comments.csv")
            efhub_df = pd.read_csv("data/processed/efhub_stats.csv")
        except FileNotFoundError:
            print("[-] Required files are missing from data/processed/")
            return

        print("[*] Quantifying text fields into metrics...")
        comments_df['sentiment_score'] = comments_df['cleaned_text'].apply(self.score_text_sentiment)
        
        calculated_profiles = []
        
        for _, player in efhub_df.iterrows():
            p_id = player['player_id']
            p_comments = comments_df[comments_df['assigned_player'] == p_id]
            
            adjusted_record = {
                "player_id": p_id,
                "display_name": player['display_name']
            }
            
            for base_stat in ["dribbling", "defending", "passing", "shooting"]:
                base_val = player[base_stat]
                related_keywords = STAT_ATTRIBUTE_MAPPING[base_stat]
                
                # Filter down to comments mentioning a specific attribute group
                stat_specific_comments = p_comments[
                    p_comments['cleaned_text'].str.lower().apply(lambda x: any(k in x for k in related_keywords))
                ]
                
                if not stat_specific_comments.empty:
                    mean_sentiment = stat_specific_comments['sentiment_score'].mean()
                else:
                    mean_sentiment = p_comments['sentiment_score'].mean() if not p_comments.empty else 0.0
                
                # Math calculation layer
                delta = mean_sentiment * BASE_ADJUSTMENT_MULTIPLIER
                delta = np.clip(delta, -MAX_STAT_ADJUSTMENT, MAX_STAT_ADJUSTMENT)
                
                adjusted_record[f"{base_stat}_base"] = base_val
                adjusted_record[f"{base_stat}_sas"] = int(np.clip(round(base_val + delta), 40, 99))
                
            calculated_profiles.append(adjusted_record)
            
        output_df = pd.DataFrame(calculated_profiles)
        output_df.to_csv("data/processed/calculated_sas_matrix.csv", index=False)
        print("[+] Processing complete. SAS matrix saved.")

if __name__ == "__main__":
    engine = eFootballSentimentEngine()
    engine.compute_sentiment_adjusted_stats()