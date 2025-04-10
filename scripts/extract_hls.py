import os
import json
import requests
import re

DATA_FOLDER = "channel_responses"
M3U_FILENAME = "channels.m3u"

# Ensure the folder exists
os.makedirs(DATA_FOLDER, exist_ok=True)

with open("yt.json", "r", encoding="utf-8") as f:
    channels = json.load(f)

playlist_entries = []

for channel in channels:
    name = channel["channel name"]
    url = channel["channel link"]

    print(f"Fetching: {name} -> {url}")
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        content = response.text
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        continue

    # Save the response content
    filename = os.path.join(DATA_FOLDER, f"{name}.html")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    # Extract hlsManifestUrl
    match = re.search(r'"hlsManifestUrl"\s*:\s*"([^"]+)"', content)
    if match:
        hls_url = match.group(1).replace("\\u0026", "&")  # handle escaped ampersands
        playlist_entries.append(f"#EXTINF:-1,{name}\n{hls_url}\n")
    else:
        print(f"No HLS URL found for {name}")

# Write the M3U file
with open(M3U_FILENAME, "w", encoding="utf-8") as f:
    f.write("#EXTM3U\n")
    f.writelines(playlist_entries)

print(f"Done! Playlist written to {M3U_FILENAME}")
