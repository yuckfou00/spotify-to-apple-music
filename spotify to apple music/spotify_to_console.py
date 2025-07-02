import spotipy
from spotipy.oauth2 import SpotifyOAuth

# Spotify credentials
CLIENT_ID = 'e1e73f45af8f445aa41af415bfaefdce'
CLIENT_SECRET = 'ebbf33c071ea4e759026266116eb1843'
REDIRECT_URI = 'http://127.0.0.1:8888/callback'
SCOPE = 'playlist-read-private'

# Connect to Spotify
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))

# Look for playlist named "<3"
target_name = "<3"
results = sp.current_user_playlists()
playlists = results['items']

# Search by name
playlist_id = None
for playlist in playlists:
    if playlist['name'].strip().lower() == target_name.strip().lower():
        playlist_id = playlist['id']
        break

if not playlist_id:
    print(f"❌ Playlist '{target_name}' not found.")
    exit()

print(f"\n📥 Getting tracks from playlist: '{target_name}'...\n")

# Fetch all tracks
tracks = []
offset = 0

while True:
    response = sp.playlist_items(playlist_id, offset=offset)
    items = response['items']
    if not items:
        break

    for item in items:
        track = item['track']
        if track:
            name = track['name']
            artist = track['artists'][0]['name']
            tracks.append(f"{name} - {artist}")
    
    offset += len(items)

# Print results
print(f"🎼 Found {len(tracks)} tracks in '{target_name}':\n")
for i, song in enumerate(tracks, start=1):
    print(f"{i}. {song}")

# Optional: Save to file
save = input("\n💾 Do you want to save this playlist to a text file? (y/n): ").strip().lower()
if save == 'y':
    filename = f"{target_name}_playlist.txt"
    with open(filename, "w", encoding="utf-8") as f:
        for i, song in enumerate(tracks, start=1):
            f.write(f"{i}. {song}\n")
    print(f"✅ Saved to {filename}")
