-- LISTENERS
INSERT INTO listeners VALUES
(1, 'Alex', 'Finland'),
(2, 'Sam', 'Sweden'),
(3, 'Jamie', 'Germany');

-- ARTISTS
INSERT INTO artists VALUES
(1, 'Taylor Swift', 'USA'),
(2, 'BTS', 'South Korea'),
(3, 'Coldplay', 'UK'),
(4, 'The Weeknd', 'Canada'),
(5, 'Billie Eilish', 'USA'),
(6, 'Adele', 'UK'),
(7, 'Lana Del Rey', 'USA'),
(8, 'Dua Lipa', 'UK'),
(9, 'Harry Styles', 'UK'),
(10, 'Sabrina Carpenter', 'USA');

-- ALBUMS
INSERT INTO albums VALUES
(1, '1989', 1, 2014),
(2, 'Midnights', 1, 2022),
(3, 'Map of the Soul: 7', 2, 2020),
(4, 'Love Yourself: Answer', 2, 2018),
(5, 'Music of the Spheres', 3, 2021),
(6, 'After Hours', 4, 2020),
(7, 'Happier Than Ever', 5, 2021),
(8, '30', 6, 2021),
(9, 'Born to Die', 7, 2012),
(10, 'Future Nostalgia', 8, 2020),
(11, 'Harrys House', 9, 2022),
(12, 'Short n Sweet', 10, 2024);

-- TRACKS
INSERT INTO tracks VALUES
(1, 'Blank Space', 1, 1, 231),
(2, 'Style', 1, 1, 231),
(3, 'Anti-Hero', 1, 2, 200),
(4, 'Midnight Rain', 1, 2, 174),
(5, 'Black Swan', 2, 3, 198),
(6, 'ON', 2, 3, 246),
(7, 'Euphoria', 2, 4, 218),
(8, 'Dynamite', 2, 4, 199),
(9, 'My Universe', 3, 5, 226),
(10, 'Higher Power', 3, 5, 211),
(11, 'Blinding Lights', 4, 6, 200),
(12, 'Save Your Tears', 4, 6, 215),
(13, 'Happier Than Ever', 5, 7, 298),
(14, 'Therefore I Am', 5, 7, 174),
(15, 'Easy On Me', 6, 8, 224),
(16, 'Oh My God', 6, 8, 225),
(17, 'Summertime Sadness', 7, 9, 265),
(18, 'Video Games', 7, 9, 281),
(19, 'Levitating', 8, 10, 203),
(20, 'As It Was', 9, 11, 167);

-- GENRES
INSERT INTO genres VALUES
(1, 'Pop'),
(2, 'K-pop'),
(3, 'Indie Pop'),
(4, 'Alternative'),
(5, 'R&B'),
(6, 'Synth-pop'),
(7, 'Rock'),
(8, 'Ballad');

-- TRACK GENRES
INSERT INTO track_genres VALUES
(1, 1), (2, 1), (3, 1), (4, 3),
(5, 2), (6, 2), (7, 2), (8, 2),
(9, 7), (10, 7),
(11, 5), (11, 6), (12, 5),
(13, 4), (14, 4),
(15, 8), (16, 1),
(17, 3), (18, 3),
(19, 1), (20, 1);

-- SYNTHETIC LISTENING HISTORY

INSERT INTO listening_history (
    listener_id,
    track_id,
    listened_at,
    duration_listened_seconds,
    completed
)
SELECT
    ((n - 1) % 3) + 1,
    t.track_id,
    NOW() - make_interval(
        days => ((n * 13) % 180),
        hours => ((n * 7) % 24)
    ),
    GREATEST(
        30,
        FLOOR(
            t.duration_seconds *
            (0.55 + (n % 5) * 0.10)
        )::INT
    ),
    (n % 4 <> 0)
FROM generate_series(1, 240) AS series(n)
JOIN tracks t
    ON t.track_id = ((n * 7 - 1) % 20) + 1;

-- Check how much data was inserted
SELECT 'listeners' AS table_name, COUNT(*) AS total
FROM listeners
UNION ALL
SELECT 'artists', COUNT(*) FROM artists
UNION ALL
SELECT 'albums', COUNT(*) FROM albums
UNION ALL
SELECT 'tracks', COUNT(*) FROM tracks
UNION ALL
SELECT 'genres', COUNT(*) FROM genres
UNION ALL
SELECT 'listening_history', COUNT(*) FROM listening_history;
