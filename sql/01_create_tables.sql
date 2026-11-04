

CREATE TABLE listeners (
    listener_id INT PRIMARY KEY,
    listener_name VARCHAR(100) NOT NULL,
    country VARCHAR(100)
);

CREATE TABLE artists (
    artist_id INT PRIMARY KEY,
    artist_name VARCHAR(150) NOT NULL,
    country VARCHAR(100)
);

CREATE TABLE albums (
    album_id INT PRIMARY KEY,
    album_name VARCHAR(150) NOT NULL,
    artist_id INT REFERENCES artists(artist_id),
    release_year INT
);

CREATE TABLE tracks (
    track_id INT PRIMARY KEY,
    track_name VARCHAR(150) NOT NULL,
    artist_id INT REFERENCES artists(artist_id),
    album_id INT REFERENCES albums(album_id),
    duration_seconds INT CHECK (duration_seconds > 0)
);

CREATE TABLE genres (
    genre_id INT PRIMARY KEY,
    genre_name VARCHAR(100) UNIQUE NOT NULL
);

-- A track can have multiple genres.
CREATE TABLE track_genres (
    track_id INT REFERENCES tracks(track_id),
    genre_id INT REFERENCES genres(genre_id),
    PRIMARY KEY (track_id, genre_id)
);

CREATE TABLE listening_history (
    listen_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    listener_id INT REFERENCES listeners(listener_id),
    track_id INT REFERENCES tracks(track_id),
    listened_at TIMESTAMP NOT NULL,
    duration_listened_seconds INT,
    completed BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_listening_time
ON listening_history(listened_at);

CREATE INDEX idx_listening_track
ON listening_history(track_id);

CREATE INDEX idx_listening_listener
ON listening_history(listener_id);
