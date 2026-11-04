
import os
import json
import time
import base64
import hashlib
import secrets
import webbrowser

from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlencode, urlparse, parse_qs

import requests
import psycopg2

from dotenv import load_dotenv


# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

load_dotenv()

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
REDIRECT_URI = os.getenv(
    "SPOTIFY_REDIRECT_URI",
    "http://127.0.0.1:8888/callback"
)

TOKEN_FILE = Path(__file__).resolve().parent.parent / "spotify_token.json"

API_BASE = "https://api.spotify.com/v1"
AUTH_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"

SCOPES = [
    "user-read-private",
    "user-read-recently-played",
    "user-top-read"
]

MAX_RECENT_PAGES = int(
    os.getenv("MAX_RECENT_PAGES", "10")
)

TIME_RANGES = [
    "short_term",
    "medium_term",
    "long_term"
]


# --------------------------------------------------
# 2. PKCE AUTHENTICATION
# --------------------------------------------------

def generate_code_verifier():
    return secrets.token_urlsafe(64)


def generate_code_challenge(verifier):
    digest = hashlib.sha256(
        verifier.encode("utf-8")
    ).digest()

    return base64.urlsafe_b64encode(
        digest
    ).decode("utf-8").rstrip("=")


class CallbackHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        params = parse_qs(
            urlparse(self.path).query
        )

        self.server.auth_code = params.get(
            "code", [None]
        )[0]

        self.server.auth_state = params.get(
            "state", [None]
        )[0]

        self.server.auth_error = params.get(
            "error", [None]
        )[0]

        if self.server.auth_code:
            message = (
                "Spotify authorization successful! "
                "You can close this browser window."
            )
        else:
            message = (
                "Spotify authorization failed. "
                "Return to your terminal."
            )

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )
        self.end_headers()

        self.wfile.write(
            f"<h2>{message}</h2>".encode()
        )

    def log_message(self, format, *args):
        return


def save_token(token_data):

    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "r") as file:
            old_token = json.load(file)

        if not token_data.get("refresh_token"):
            token_data["refresh_token"] = old_token.get(
                "refresh_token"
            )

    token_data["expires_at"] = (
        time.time() + token_data["expires_in"]
    )

    with open(TOKEN_FILE, "w") as file:
        json.dump(token_data, file, indent=4)


def load_token():

    if TOKEN_FILE.exists():
        with open(TOKEN_FILE, "r") as file:
            return json.load(file)

    return None


def authorize():

    verifier = generate_code_verifier()
    challenge = generate_code_challenge(verifier)

    state = secrets.token_urlsafe(24)

    params = {
        "client_id": CLIENT_ID,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": " ".join(SCOPES),
        "code_challenge_method": "S256",
        "code_challenge": challenge,
        "state": state
    }

    authorization_url = (
        AUTH_URL + "?" + urlencode(params)
    )

    server = HTTPServer(
        ("127.0.0.1", 8888),
        CallbackHandler
    )

    server.timeout = 180

    print("\nOpening Spotify login...")
    webbrowser.open(authorization_url)

    print(
        "Please log in and approve the requested permissions."
    )

    server.handle_request()

    code = getattr(server, "auth_code", None)
    returned_state = getattr(
        server, "auth_state", None
    )
    error = getattr(server, "auth_error", None)

    server.server_close()

    if error:
        raise RuntimeError(
            f"Spotify authorization error: {error}"
        )

    if not code:
        raise RuntimeError(
            "No authorization code received. "
            "Try running the script again."
        )

    if returned_state != state:
        raise RuntimeError(
            "OAuth state mismatch. Authorization rejected."
        )

    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": REDIRECT_URI,
            "code_verifier": verifier
        },
        timeout=30
    )

    response.raise_for_status()

    token_data = response.json()

    save_token(token_data)

    print("Spotify authentication successful!")


def refresh_token():

    token_data = load_token()

    if not token_data:
        authorize()
        return load_token()

    refresh = token_data.get("refresh_token")

    if not refresh:
        authorize()
        return load_token()

    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": CLIENT_ID,
            "grant_type": "refresh_token",
            "refresh_token": refresh
        },
        timeout=30
    )

    response.raise_for_status()

    new_token = response.json()

    if "refresh_token" not in new_token:
        new_token["refresh_token"] = refresh

    save_token(new_token)

    return new_token


def get_valid_token():

    token_data = load_token()

    if not token_data:
        authorize()
        token_data = load_token()

    if time.time() >= token_data.get(
        "expires_at", 0
    ) - 60:
        token_data = refresh_token()

    return token_data["access_token"]


# --------------------------------------------------
# 3. SPOTIFY API CLIENT
# --------------------------------------------------

class SpotifyClient:

    def __init__(self):
        self.access_token = get_valid_token()

    def get(self, endpoint, params=None):

        url = API_BASE + endpoint

        response = requests.get(
            url,
            headers={
                "Authorization": (
                    f"Bearer {self.access_token}"
                )
            },
            params=params,
            timeout=30
        )

        if response.status_code == 401:
            token_data = refresh_token()
            self.access_token = token_data[
                "access_token"
            ]

            response = requests.get(
                url,
                headers={
                    "Authorization": (
                        f"Bearer {self.access_token}"
                    )
                },
                params=params,
                timeout=30
            )

        if response.status_code == 403:
            raise RuntimeError(
                "Spotify denied access. Check your "
                "app permissions, scopes and Development "
                "Mode endpoint access."
            )

        if response.status_code == 429:
            wait = int(
                response.headers.get(
                    "Retry-After", "5"
                )
            )
            print(f"Rate limited. Waiting {wait}s...")
            time.sleep(wait)

            return self.get(endpoint, params)

        response.raise_for_status()

        return response.json()


# --------------------------------------------------
# 4. DATABASE CONNECTION
# --------------------------------------------------

def connect_database():

    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


# --------------------------------------------------
# 5. SAVE ARTISTS AND TRACKS
# --------------------------------------------------

def save_artist(cursor, artist):

    artist_id = artist.get("id")

    if not artist_id:
        return

    cursor.execute("""
        INSERT INTO spotify_artists (
            spotify_artist_id,
            artist_name
        )
        VALUES (%s, %s)
        ON CONFLICT (spotify_artist_id)
        DO UPDATE SET
            artist_name = EXCLUDED.artist_name;
    """, (
        artist_id,
        artist.get("name", "Unknown")
    ))


def save_track(cursor, track):

    track_id = track.get("id")

    if not track_id:
        return None

    album = track.get("album") or {}

    cursor.execute("""
        INSERT INTO spotify_tracks (
            spotify_track_id,
            track_name,
            album_name,
            duration_ms,
            spotify_uri,
            spotify_url
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (spotify_track_id)
        DO UPDATE SET
            track_name = EXCLUDED.track_name,
            album_name = EXCLUDED.album_name,
            duration_ms = EXCLUDED.duration_ms,
            spotify_uri = EXCLUDED.spotify_uri,
            spotify_url = EXCLUDED.spotify_url;
    """, (
        track_id,
        track.get("name", "Unknown"),
        album.get("name"),
        track.get("duration_ms"),
        track.get("uri"),
        (track.get("external_urls") or {}).get(
            "spotify"
        )
    ))

    for position, artist in enumerate(
        track.get("artists", [])
    ):

        save_artist(cursor, artist)

        if artist.get("id"):
            cursor.execute("""
                INSERT INTO spotify_track_artists (
                    spotify_track_id,
                    spotify_artist_id,
                    artist_position
                )
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (
                track_id,
                artist["id"],
                position
            ))

    return track_id


# --------------------------------------------------
# 6. IMPORT RECENTLY PLAYED TRACKS
# --------------------------------------------------

def import_recent_tracks(
    spotify,
    cursor,
    listener_id
):

    print("\nFetching recent listening history...")

    before = None
    total_inserted = 0

    for page_number in range(
        1, MAX_RECENT_PAGES + 1
    ):

        params = {"limit": 50}

        if before:
            params["before"] = before

        data = spotify.get(
            "/me/player/recently-played",
            params=params
        )

        items = data.get("items", [])

        if not items:
            break

        page_inserted = 0

        for item in items:

            track = item.get("track")

            if not track:
                continue

            track_id = save_track(
                cursor, track
            )

            if not track_id:
                continue

            context = item.get("context") or {}

            cursor.execute("""
                INSERT INTO spotify_streams (
                    listener_id,
                    spotify_track_id,
                    played_at,
                    context_type,
                    context_uri
                )
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING;
            """, (
                listener_id,
                track_id,
                item.get("played_at"),
                context.get("type"),
                context.get("uri")
            ))

            if cursor.rowcount > 0:
                page_inserted += 1

        total_inserted += page_inserted

        print(
            f"Page {page_number}: "
            f"{page_inserted} new listening events"
        )

        before = (
            data.get("cursors") or {}
        ).get("before")

        if not before:
            break

    print(
        f"Total new listening events: {total_inserted}"
    )


# --------------------------------------------------
# 7. IMPORT TOP ARTISTS AND TRACKS
# --------------------------------------------------

def import_top_items(
    spotify,
    cursor,
    listener_id
):

    print("\nFetching top artists and tracks...")

    for item_type in ["artists", "tracks"]:

        for time_range in TIME_RANGES:

            data = spotify.get(
                f"/me/top/{item_type}",
                params={
                    "limit": 50,
                    "time_range": time_range
                }
            )

            items = data.get("items", [])

            for rank, item in enumerate(
                items, start=1
            ):

                if item_type == "artists":

                    save_artist(cursor, item)

                    item_id = item.get("id")
                    item_name = item.get("name")

                    artist_names = None
                    album_name = None

                    item_type_db = "artist"

                else:

                    save_track(cursor, item)

                    item_id = item.get("id")
                    item_name = item.get("name")

                    artist_names = ", ".join(
                        artist.get("name", "")
                        for artist in item.get(
                            "artists", []
                        )
                    )

                    album_name = (
                        item.get("album") or {}
                    ).get("name")

                    item_type_db = "track"

                if not item_id:
                    continue

                cursor.execute("""
                    INSERT INTO spotify_top_items (
                        listener_id,
                        item_type,
                        time_range,
                        spotify_item_id,
                        item_name,
                        artist_names,
                        album_name,
                        item_rank
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (
                        listener_id,
                        item_type,
                        time_range,
                        item_rank,
                        snapshot_date
                    )
                    DO UPDATE SET
                        spotify_item_id =
                            EXCLUDED.spotify_item_id,
                        item_name = EXCLUDED.item_name,
                        artist_names = EXCLUDED.artist_names,
                        album_name = EXCLUDED.album_name;
                """, (
                    listener_id,
                    item_type_db,
                    time_range,
                    item_id,
                    item_name,
                    artist_names,
                    album_name,
                    rank
                ))

            print(
                f"Imported {len(items)} {item_type} "
                f"for {time_range}"
            )


# --------------------------------------------------
# 8. MAIN PROGRAM
# --------------------------------------------------

def main():

    if not CLIENT_ID:
        raise ValueError(
            "Add SPOTIFY_CLIENT_ID to your .env file."
        )

    print("Music Taste Archaeology")
    print("-----------------------")

    spotify = SpotifyClient()

    print("Connected to Spotify!")

    profile = spotify.get("/me")

    spotify_user_id = profile["id"]
    username = (
        profile.get("display_name")
        or spotify_user_id
    )

    print(f"Spotify account: {username}")

    connection = connect_database()

    try:

        with connection.cursor() as cursor:

            cursor.execute("""
                INSERT INTO spotify_listeners (
                    spotify_user_id,
                    username
                )
                VALUES (%s, %s)
                ON CONFLICT (spotify_user_id)
                DO UPDATE SET
                    username = EXCLUDED.username
                RETURNING listener_id;
            """, (
                spotify_user_id,
                username
            ))

            listener_id = cursor.fetchone()[0]

            import_recent_tracks(
                spotify,
                cursor,
                listener_id
            )

            import_top_items(
                spotify,
                cursor,
                listener_id
            )

        connection.commit()

        print("\nImport completed successfully!")

    except Exception:

        connection.rollback()
        raise

    finally:

        connection.close()


if __name__ == "__main__":
    main()
