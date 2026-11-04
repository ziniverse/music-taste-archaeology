
-- Which artists are listened to the most?

SELECT
    a.artist_name,
    COUNT(*) AS total_listens
FROM listening_history lh
JOIN tracks t
    ON lh.track_id = t.track_id
JOIN artists a
    ON t.artist_id = a.artist_id
GROUP BY a.artist_name
ORDER BY total_listens DESC;


-- What are the most played songs?

SELECT
    t.track_name,
    a.artist_name,
    COUNT(*) AS play_count
FROM listening_history lh
JOIN tracks t
    ON lh.track_id = t.track_id
JOIN artists a
    ON t.artist_id = a.artist_id
GROUP BY t.track_name, a.artist_name
ORDER BY play_count DESC
LIMIT 10;


-- Which genres are listened to the most?

SELECT
    g.genre_name,
    COUNT(DISTINCT lh.listen_id) AS total_listens
FROM listening_history lh
JOIN track_genres tg
    ON lh.track_id = tg.track_id
JOIN genres g
    ON tg.genre_id = g.genre_id
GROUP BY g.genre_name
ORDER BY total_listens DESC;


-- At what time of day do people listen to music?

SELECT
    CASE
        WHEN EXTRACT(HOUR FROM listened_at) BETWEEN 5 AND 11
            THEN 'Morning'
        WHEN EXTRACT(HOUR FROM listened_at) BETWEEN 12 AND 16
            THEN 'Afternoon'
        WHEN EXTRACT(HOUR FROM listened_at) BETWEEN 17 AND 21
            THEN 'Evening'
        ELSE 'Night'
    END AS time_of_day,
    COUNT(*) AS total_listens
FROM listening_history
GROUP BY time_of_day
ORDER BY total_listens DESC;


-- How has listening activity changed month by month?

SELECT
    DATE_TRUNC('month', listened_at)::DATE AS listening_month,
    COUNT(*) AS total_listens
FROM listening_history
GROUP BY listening_month
ORDER BY listening_month;


-- Which artists are most popular for each listener?


WITH artist_listens AS (
    SELECT
        l.listener_name,
        a.artist_name,
        COUNT(*) AS total_listens
    FROM listening_history lh
    JOIN listeners l
        ON lh.listener_id = l.listener_id
    JOIN tracks t
        ON lh.track_id = t.track_id
    JOIN artists a
        ON t.artist_id = a.artist_id
    GROUP BY l.listener_name, a.artist_name
),
ranked_artists AS (
    SELECT
        *,
        RANK() OVER (
            PARTITION BY listener_name
            ORDER BY total_listens DESC
        ) AS artist_rank
    FROM artist_listens
)
SELECT *
FROM ranked_artists
WHERE artist_rank <= 3
ORDER BY listener_name, artist_rank;

-- Which songs have the highest completion rate?

SELECT
    t.track_name,
    a.artist_name,
    COUNT(*) AS total_plays,
    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE lh.completed = TRUE
        ) / COUNT(*),
        2
    ) AS completion_percentage
FROM listening_history lh
JOIN tracks t
    ON lh.track_id = t.track_id
JOIN artists a
    ON t.artist_id = a.artist_id
GROUP BY t.track_name, a.artist_name
ORDER BY completion_percentage DESC;


-- How much time has each listener spent listening?

SELECT
    l.listener_name,
    ROUND(
        SUM(lh.duration_listened_seconds) / 3600.0,
        2
    ) AS listening_hours
FROM listening_history lh
JOIN listeners l
    ON lh.listener_id = l.listener_id
GROUP BY l.listener_name
ORDER BY listening_hours DESC;
