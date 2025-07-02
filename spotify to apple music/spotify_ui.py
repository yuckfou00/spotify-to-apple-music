import tkinter as tk
from tkinter import ttk, messagebox
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import webbrowser
import urllib.parse

# Spotify credentials
CLIENT_ID = 'your CLIENT_ID '
CLIENT_SECRET = 'your CLIENT_SECRET'
REDIRECT_URI = '...'
SCOPE = 'playlist-read-private'

# Initialize Spotify API
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=SCOPE
))

# Track song index state between clicks
search_progress = {
    "playlist_id": None,
    "songs": [],
    "index": 0
}

def get_playlists():
    results = sp.current_user_playlists()
    return {p['name']: p['id'] for p in results['items']}

def get_tracks(playlist_id):
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
    return tracks

def run_ui():
    playlists = get_playlists()

    root = tk.Tk()
    root.title("Spotify Playlist Viewer")
    root.geometry("700x550")

    ttk.Label(root, text="Choose a Playlist:", font=("Arial", 12)).pack(pady=10)

    playlist_var = tk.StringVar()
    playlist_dropdown = ttk.Combobox(root, textvariable=playlist_var, state="readonly")
    playlist_dropdown['values'] = list(playlists.keys())
    playlist_dropdown.pack(pady=5)

    text_box = tk.Text(root, wrap=tk.WORD, height=20)
    text_box.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def fetch_songs():
        selected_name = playlist_var.get()
        if not selected_name:
            messagebox.showwarning("No Playlist", "Please select a playlist.")
            return
        playlist_id = playlists[selected_name]
        songs = get_tracks(playlist_id)

        # update search progress
        search_progress["playlist_id"] = playlist_id
        search_progress["songs"] = songs
        search_progress["index"] = 0

        text_box.delete('1.0', tk.END)
        for i, song in enumerate(songs, start=1):
            text_box.insert(tk.END, f"{i}. {song}\n")

    def export_to_txt():
        selected_name = playlist_var.get()
        if not selected_name:
            messagebox.showwarning("No Playlist", "Please select a playlist.")
            return
        playlist_id = playlists[selected_name]
        songs = get_tracks(playlist_id)

        filename = f"{selected_name}_playlist.txt"
        with open(filename, "w", encoding="utf-8") as f:
            for i, song in enumerate(songs, start=1):
                f.write(f"{i}. {song}\n")
        messagebox.showinfo("Exported", f"Playlist saved to {filename}")

    def search_on_apple_music():
        selected_name = playlist_var.get()
        if not selected_name:
            messagebox.showwarning("No Playlist", "Please select a playlist.")
            return

        playlist_id = playlists[selected_name]

        # Check if it's the same playlist as last time
        if search_progress["playlist_id"] != playlist_id:
            search_progress["playlist_id"] = playlist_id
            search_progress["songs"] = get_tracks(playlist_id)
            search_progress["index"] = 0

        songs = search_progress["songs"]
        start = search_progress["index"]
        end = start + 10
        next_batch = songs[start:end]

        if not next_batch:
            messagebox.showinfo("Done", "✅ All songs from this playlist have been opened.")
            return

        confirm = messagebox.askyesno(
            "Apple Music Search",
            f"Open Apple Music search for songs {start+1} to {min(end, len(songs))}?"
        )
        if not confirm:
            return

        for song in next_batch:
            query = urllib.parse.quote(song)
            url = f"https://music.apple.com/us/search?term={query}"
            webbrowser.open_new_tab(url)

        search_progress["index"] = end

    fetch_button = ttk.Button(root, text="Fetch Songs", command=fetch_songs)
    fetch_button.pack(pady=5)

    export_button = ttk.Button(root, text="Export to TXT", command=export_to_txt)
    export_button.pack(pady=5)

    search_button = ttk.Button(root, text="Search on Apple Music (10 by 10)", command=search_on_apple_music)
    search_button.pack(pady=5)

    root.mainloop()

# Run the UI
run_ui()
