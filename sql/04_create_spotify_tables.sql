

CREATE TABLE spotify_listeners (
    listener_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    spotify_user_id VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(200)
);

CREATE TABLE spotify_artists (
    spotify_artist_id VARCHAR(100) PRIMARY KEY,
    artist_name VARCHAR(200) NOT NULL
);

CREATE TABLE spotify_tracks (
    spotify_track_id VARCHAR(100) PRIMARY KEY,
    track_name VARCHAR(300) NOT NULL,
    album_name VARCHAR(300),
    duration_ms INTEGER,
    spotify_uri VARCHAR(200),
    spotify_url TEXT
);

-- A track can have multiple artists.
CREATE TABLE spotify_track_artists (
    spotify_track_id VARCHAR(100)
        REFERENCES spotify_tracks(spotify_track_id),
    spotify_artist_id VARCHAR(100)
        REFERENCES spotify_artists(spotify_artist_id),
    artist_position INTEGER,
    PRIMARY KEY (spotify_track_id, spotify_artist_id)
);

-- Each row represents a listening event.
CREATE TABLE spotify_streams (
    stream_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    listener_id INTEGER REFERENCES spotify_listeners(listener_id),
    spotify_track_id VARCHAR(100)
        REFERENCES spotify_tracks(spotify_track_id),
    played_at TIMESTAMPTZ NOT NULL,
    context_type VARCHAR(100),
    context_uri VARCHAR(200),

    UNIQUE (listener_id, spotify_track_id, played_at)
);

-- Stores rankings returned by Spotify's top-items endpoint.
CREATE TABLE spotify_top_items (
    top_item_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    listener_id INTEGER REFERENCES spotify_listeners(listener_id),
    item_type VARCHAR(20) NOT NULL
        CHECK (item_type IN ('artist', 'track')),
    time_range VARCHAR(20) NOT NULL
        CHECK (time_range IN (
            'short_term',
            'medium_term',
            'long_term'
        )),
    spotify_item_id VARCHAR(100) NOT NULL,
    item_name VARCHAR(300) NOT NULL,
    artist_names TEXT,
    album_name VARCHAR(300),
    item_rank INTEGER NOT NULL,
    snapshot_date DATE NOT NULL DEFAULT CURRENT_DATE,

    UNIQUE (
        listener_id,
        item_type,
        time_range,
        item_rank,
        snapshot_date
    )
);

-- Indexes for analysis
CREATE INDEX idx_spotify_streams_time
ON spotify_streams(played_at);

CREATE INDEX idx_spotify_streams_track
ON spotify_streams(spotify_track_id);

CREATE INDEX idx_spotify_tracks_name
ON spotify_tracks(track_name);

CREATE INDEX idx_spotify_artists_name
ON spotify_artists(artist_name);

CREATE INDEX idx_spotify_top_items_type
ON spotify_top_items(item_type, time_range);
