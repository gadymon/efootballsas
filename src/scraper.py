import sys
import os
# Adds the root directory (one level up from 'src') to the Python path list
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
import pandas as pd
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from config.settings import YOUTUBE_API_KEY, TARGET_CHANNEL_ID

def get_uploads_playlist_id(channel_id, youtube):
    request = youtube.channels().list(part="contentDetails", id=channel_id)
    response = request.execute()
    return response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

def fetch_all_video_ids(playlist_id, youtube):
    video_ids = []
    next_page_token = None
    
    while True:
        request = youtube.playlistItems().list(
            part="snippet",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page_token
        )
        response = request.execute()
        for item in response['items']:
            video_ids.append(item['snippet']['resourceId']['videoId'])
            
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    return video_ids

def scrape_channel_comments():
    if YOUTUBE_API_KEY == "YOUR_ACTUAL_YOUTUBE_API_KEY":
        print("[!] Warning: Please replace placeholder API key in config/settings.py")
        return pd.DataFrame()

    youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
    
    try:
        uploads_id = get_uploads_playlist_id(TARGET_CHANNEL_ID, youtube)
        video_ids = fetch_all_video_ids(uploads_id, youtube)
    except Exception as e:
        print(f"[-] Failed to access channel profile layout: {e}")
        return pd.DataFrame()
        
    compiled_comments = []
    print(f"[+] Isolated {len(video_ids)} videos. Extracting comment fields...")

    for i, v_id in enumerate(video_ids):
        # Prevent hitting API thresholds on massive channels
        if i >= 20: 
            print("[*] Iteration cap hit to preserve daily developer quota thresholds.")
            break
            
        try:
            request = youtube.commentThreads().list(
                part="snippet", videoId=v_id, maxResults=100, textFormat="plainText"
            )
            while request:
                res = request.execute()
                for item in res['items']:
                    snap = item['snippet']['topLevelComment']['snippet']
                    compiled_comments.append({
                        "video_id": v_id,
                        "author": snap['authorDisplayName'],
                        "comment_text": snap['textDisplay'],
                        "likes": snap['likeCount']
                    })
                request = youtube.commentThreads().list_next(request, res)
        except HttpError:
            continue # Skip videos with disabled comments safely
        time.sleep(0.2)

    df = pd.DataFrame(compiled_comments)
    if not df.empty:
        df.to_csv("data/raw/youtube_comments.csv", index=False)
    return df

if __name__ == "__main__":
    scrape_channel_comments()