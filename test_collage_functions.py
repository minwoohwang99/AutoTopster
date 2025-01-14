import os
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Spotify API Authentication
def authenticate_spotify():
    return Spotify(auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
        scope="user-top-read"
    ))

# Fetch user's top tracks
def fetch_top_tracks(spotify_client, limit, time_range='short_term'):
    results = spotify_client.current_user_top_tracks(limit=limit, time_range=time_range)
    return [{"name": track["name"], "artist": track["artists"][0]["name"]} for track in results["items"]]

# Fetch user's top albums
def fetch_top_albums(spotify_client, limit, time_range='short_term'):
    results = spotify_client.current_user_top_artists(limit=limit, time_range=time_range)
    albums = []
    for artist in results['items']:
        artist_albums = spotify_client.artist_albums(artist['id'], album_type='album', limit=1)
        if artist_albums['items']:
            albums.append({
                "name": artist_albums['items'][0]['name'],
                "artist": artist['name']
            })
        if len(albums) >= limit:
            break
    return albums

# Main script
def main():
    sp = authenticate_spotify()

    # Step 1: Select content type
    print("Select Content Type:")
    print("1. Songs")
    print("2. Albums")
    content_type = int(input("Enter 1 or 2: "))
    if content_type == 1:
        content_label = "Songs"
    elif content_type == 2:
        content_label = "Albums"
    else:
        print("Invalid input. Defaulting to Songs.")
        content_type = 1
        content_label = "Songs"

    # Step 2: Select time range
    print("\nSelect Time Range:")
    print("1. Last 4 weeks")
    print("2. Last 6 months")
    print("3. All time")
    time_range_input = int(input("Enter 1, 2, or 3: "))
    if time_range_input == 1:
        time_range = 'short_term'
        time_label = "Last 4 weeks"
    elif time_range_input == 2:
        time_range = 'medium_term'
        time_label = "Last 6 months"
    elif time_range_input == 3:
        time_range = 'long_term'
        time_label = "All time"
    else:
        print("Invalid input. Defaulting to Last 4 weeks.")
        time_range = 'short_term'
        time_label = "Last 4 weeks"

    # Step 3: Select grid size
    print("\nSelect Grid Size:")
    print("1. 3x3")
    print("2. 4x4")
    print("3. 5x5")
    grid_size_input = int(input("Enter 1, 2, or 3: "))
    if grid_size_input == 1:
        grid_size = 3
    elif grid_size_input == 2:
        grid_size = 4
    elif grid_size_input == 3:
        grid_size = 5
    else:
        print("Invalid input. Defaulting to 3x3.")
        grid_size = 3

    # Step 4: Fetch data
    limit = grid_size * grid_size
    if content_type == 1:
        print(f"\nFetching your top {limit} {content_label} ({time_label})...\n")
        top_items = fetch_top_tracks(sp, limit, time_range)
    elif content_type == 2:
        print(f"\nFetching your top {limit} {content_label} ({time_label})...\n")
        top_items = fetch_top_albums(sp, limit, time_range)

    # Step 5: Print the results
    for idx, item in enumerate(top_items, start=1):
        print(f"{idx}. {item['name']} by {item['artist']}")

    print("\nTest completed. If results are correct, your functions are working properly.")

# Entry point
if __name__ == "__main__":
    main()
