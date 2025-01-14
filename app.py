from flask import Flask, redirect, request, send_file, render_template, session, jsonify
from create_collage import authenticate_spotify, fetch_top_tracks, fetch_top_albums, fetch_top_artists, download_album_cover, create_topster_collage
import os
from urllib.parse import urlencode
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Ensure directories exist
COVERS_DIR = "covers"
COLLAGES_DIR = "collages"
os.makedirs(COVERS_DIR, exist_ok=True)
os.makedirs(COLLAGES_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    # Collect user-selected options from the form
    grid_size = request.args.get('grid_size', '3')
    time_range = request.args.get('time_range', 'short_term')
    content_type = request.args.get('content_type', 'songs')

    # Create a state parameter to pass user options securely
    state = urlencode({'grid_size': grid_size, 'time_range': time_range, 'content_type': content_type})

    # Initialize Spotify OAuth with state
    sp_oauth = SpotifyOAuth(client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),  # Use the exact redirect URI
                            scope="user-top-read",
                            state=state)
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)

@app.route('/collages/<filename>')
def serve_collage(filename):
    return send_file(os.path.join(COLLAGES_DIR, filename))

@app.route('/callback')
def callback():
    sp_oauth = SpotifyOAuth(client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                            redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
                            scope="user-top-read")

    # Retrieve Spotify authorization code
    code = request.args.get('code')
    state = request.args.get('state')  # Retrieve the state parameter
    token_info = sp_oauth.get_access_token(code)
    sp = Spotify(auth=token_info if isinstance(token_info, str) else token_info['access_token'])

    # Parse the state parameter to retrieve user-selected options
    from urllib.parse import parse_qs
    options = parse_qs(state)
    grid_size = int(options.get('grid_size', [3])[0])  # Default to 3
    time_range = options.get('time_range', ['short_term'])[0]
    content_type = options.get('content_type', ['songs'])[0]

    # Fetch top items
    limit = grid_size * grid_size
    if content_type == 'songs':
        top_items = fetch_top_tracks(sp, limit, time_range)
        image_urls = [item['album']['images'][0]['url'] for item in top_items]
        display_data = [{"name": item['name'], "artist": item['artists'][0]['name']} for item in top_items]
    elif content_type == 'artists':
        top_items = fetch_top_artists(sp, limit, time_range)
        image_urls = [artist['image'] for artist in top_items]
        display_data = [{"name": artist['name'], "genres": ', '.join(artist['genres'])} for artist in top_items]

    # Download album covers
    image_files = []
    for idx, url in enumerate(image_urls):
        file_name = os.path.join(COVERS_DIR, f"album_{idx + 1}.jpg")
        download_album_cover(url, file_name)
        image_files.append(file_name)

    # Create collage
    output_file = os.path.join(COLLAGES_DIR, "topster_collage.jpg")
    create_topster_collage(image_files, output_file, grid_size)

    # Pass the collage and display data to the template
    return render_template('collage.html', collage_filename=os.path.basename(output_file), display_data=display_data, content_type=content_type)

if __name__ == '__main__':
    app.run(debug=True)
