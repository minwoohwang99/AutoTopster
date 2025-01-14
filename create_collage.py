import os
import requests
from PIL import Image
from dotenv import load_dotenv
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

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
    return results['items']

# Fetch user's top albums
def fetch_top_albums(spotify_client, limit, time_range='short_term'):
    results = spotify_client.current_user_top_artists(limit=limit, time_range=time_range)
    albums = []
    for artist in results['items']:
        artist_albums = spotify_client.artist_albums(artist['id'], album_type='album', limit=1)
        if artist_albums['items']:
            albums.append(artist_albums['items'][0])  # Add the first album
        if len(albums) >= limit:
            break
    return albums

def fetch_top_artists(spotify_client, limit, time_range='short_term'):
    # Fetch the user's top artists
    results = spotify_client.current_user_top_artists(limit=limit, time_range=time_range)
    
    # Extract relevant artist information
    top_artists = []
    for artist in results['items']:
        top_artists.append({
            "name": artist["name"],                # Artist's name
            "image": artist["images"][0]["url"],  # Artist's profile picture (largest image)
            "popularity": artist["popularity"],   # Optional: Artist's popularity score
            "genres": artist["genres"]            # Optional: Artist's genres
        })
    
    return top_artists


# Download album cover
def download_album_cover(url, file_name):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)

# Create a Topster collage
def create_topster_collage(image_files, output_file, grid_side=3):
    image_size = 300  # Each image will be resized to 300x300 pixels
    canvas_size = grid_side * image_size
    collage = Image.new('RGB', (canvas_size, canvas_size))
    for idx, image_file in enumerate(image_files):
        img = Image.open(image_file).resize((image_size, image_size))
        x = (idx % grid_side) * image_size
        y = (idx // grid_side) * image_size
        collage.paste(img, (x, y))
    collage.save(output_file)
