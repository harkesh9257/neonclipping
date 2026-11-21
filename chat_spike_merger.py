"""Fetch live stream chat replay (Twitch & YouTube) and compute chat hype density.

When processing finished live streams (VODs), chat spike velocity tells us exactly
when funny moments, fails, or epic plays happened based on audience reaction:
e.g. bursts of 'LMAO', 'LOL', 'W', 'OMG', 'HAIL', 'BHAIII', '???', 'GG'.
"""
import json
import re
import subprocess
from pathlib import Path
import numpy as np

def extract_yt_chat_velocity(url_or_id, duration, bucket_seconds=10):
    """
    Attempts to download chat replay via yt-dlp or extract live chat json.
    Returns: numpy array of message counts per bucket_seconds
    """
    total_buckets = max(1, int(np.ceil(duration / bucket_seconds)))
    counts = np.zeros(total_buckets, dtype=np.float32)
    
    # Extract video id
    m = re.search(r'(?:v=|/live/|youtu\.be/)([A-Za-z0-9_-]{11})', str(url_or_id))
    vid = m.group(1) if m else str(url_or_id)
    if not len(vid) == 11:
        return counts

    # Check if chat was already extracted
    chat_file = Path(f"/tmp/chat_{vid}.json")
    if not chat_file.exists():
        chat_file = Path(f"data/chat_{vid}.json")

    # If yt-dlp has live_chat replay:
    cmd = [
        'yt-dlp', '--skip-download', '--write-subs', '--sub-langs', 'live_chat',
        '--output', f'data/chat_{vid}.%(ext)s', f'https://www.youtube.com/watch?v={vid}'
    ]
    try:
        subprocess.run(cmd, capture_output=True, timeout=30)
    except Exception:
        pass

    # Look for saved live_chat.json
    found = list(Path('data').glob(f'chat_{vid}.*live_chat*'))
    if not found:
        return counts

    try:
        with open(found[0], 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    j = json.loads(line)
                    # Get offset time in microseconds
                    offset = None
                    replay = j.get('replayChatItemAction', {})
                    actions = replay.get('actions', [])
                    for act in actions:
                        item = act.get('addChatItemAction', {}).get('item', {})
                        renderer = item.get('liveChatTextMessageRenderer') or item.get('liveChatPaidMessageRenderer')
                        if renderer:
                            ts_usec = int(j.get('videoOffsetTimeMsec', 0))
                            offset = ts_usec / 1000.0
                            break
                    if offset is not None and 0 <= offset < duration:
                        b = int(offset // bucket_seconds)
                        if b < total_buckets:
                            counts[b] += 1
                except Exception:
                    continue
    except Exception:
        pass

    return counts

def merge_chat_spikes(candidates, chat_counts, bucket_seconds=10):
    """
    Boost candidate viral score if it coincides with a chat hype spike.
    """
    if len(chat_counts) == 0 or np.max(chat_counts) == 0:
        return candidates

    mean_chat = np.mean(chat_counts)
    std_chat = np.std(chat_counts) or 1.0

    for c in candidates:
        start_b = int(c['start'] // bucket_seconds)
        end_b = int(c['end'] // bucket_seconds) + 1
        window = chat_counts[start_b:end_b]
        if len(window) > 0:
            peak = float(np.max(window))
            # If chat spiked above mean + 2*sigma
            if peak > mean_chat + 1.8 * std_chat:
                hype_boost = min(25, int(15 * (peak / max(1.0, mean_chat))))
                c['score'] = min(99, c.get('score', 50) + hype_boost)
                c['reason'] = (c.get('reason', '') + f" [🔥 Chat Spike {int(peak)} msgs]").strip()
                if 'features' in c and isinstance(c['features'], dict):
                    c['features']['chat_hype'] = round(peak / max(1.0, mean_chat), 2)
    return candidates
