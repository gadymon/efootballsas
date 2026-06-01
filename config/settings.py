# config/settings.py
import os
import json

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "AIzaSyC76rko8UuGEymopyy8Q1Vgdop_J7jJ2zQ")
TARGET_CHANNEL_ID = "UCvzTJH6G9bH5nCQ1Hfb8nGg"

MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
MAX_TOKEN_LENGTH = 512

GAMING_SLANG_DICTIONARY = {
    "positive_boosts": ["beast", "cyborg", "broken", "unreal", "love", "clutch", "endgame", "cheatcode", "meta", "glitch", "underated", "starter", "fire", "lit","must have"],
    "negative_nerfs": ["truck", "clunky", "fake", "ghost", "trash", "fraud", "stiff" ]
}

STAT_ATTRIBUTE_MAPPING = {
    "dribbling": ["dribbling", "clunky", "truck", "turn", "balance", "stiff", "nimble", "agile", "speed", "pace"],
    "defending": ["tackling", "defense", "intercept", "reach", "prowess", "aggression", "interception"],
    "passing": ["pass", "crossing", "assist", "throughball", "vision", "crossing"],
    "shooting": ["finishing", "shoot", "goal", "clinical", "missed", "striker", "heading", "header"]
}

MAX_STAT_ADJUSTMENT = 5
BASE_ADJUSTMENT_MULTIPLIER = 4.0

# --- DYNAMIC PLAYER DICTIONARY LAYER ---
DYNAMIC_JSON_PATH = os.path.join("data", "processed", "dynamic_players.json")

def load_player_dictionary():
    if os.path.exists(DYNAMIC_JSON_PATH):
        try:
            with open(DYNAMIC_JSON_PATH, "r") as f:
                return json.load(f)
        except Exception:
            pass
    # Safe empty dictionary initialization before first pipeline build
    return {}

PLAYER_DICTIONARY = load_player_dictionary()
