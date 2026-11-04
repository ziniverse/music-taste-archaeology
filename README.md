
# Music Taste Archaeology
### Exploring Personal Music Listening Habits with Python, PostgreSQL, SQL and Power BI

## Overview

**Music Taste Archaeology** is a personal data analytics project that explores music listening habits and patterns using data from the Spotify Web API.

The project combines Python, PostgreSQL, SQL and Power BI to collect, store, analyse and visualise music-related data. It explores questions such as:

- Which artists and tracks appear most frequently in my listening history?
- How does my listening activity change over time?
- At what times of the day am I most likely to listen to music?
- Which days of the week have the highest listening activity?
- How does my music taste differ across Spotify's short-term, medium-term and long-term rankings?

The goal is to turn personal music data into meaningful insights while demonstrating practical skills in data collection, database design, SQL querying and data visualisation.

## Technologies

| Technology | Purpose |
|---|---|
| Python | Data collection and API integration |
| Spotify Web API | Retrieving listening history and top music rankings |
| PostgreSQL | Storing and managing structured data |
| SQL | Querying, transforming and analysing data |
| Power BI | Building interactive dashboards and visualisations |
| Git & GitHub | Version control and project documentation |

## Project Structure

```text
music_archeology_sql_project/
│
├── sql/
│   ├── 01_create_tables.sql
│   ├── 02_insert_data.sql
│   ├── 03_fictional_analysis.sql
│   ├── 04_create_spotify_tables.sql
│   └── 05_spotify_analysis.sql
│
├── scripts/
│   └── import_spotify.py
│
├── powerbi/
│   └── screenshots/
│       ├── overview.png
│       ├── listening_patterns.png
│       └── music_evolution.png
│
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Data Collection

Data is collected through the Spotify Web API using Python.

Authentication is implemented using the OAuth 2.0 Authorization Code with PKCE flow.

The Python importer retrieves:

- **Recently played tracks:** Tracks available through Spotify's recently played endpoint.
- **Top artists:** Top artist rankings across short-term, medium-term and long-term time ranges.
- **Top tracks:** Top track rankings across short-term, medium-term and long-term time ranges.
- **Track and artist metadata:** Track names, artist names, album names, durations and Spotify links.

The importer stores the retrieved data in a local PostgreSQL database.

### Data limitations

Spotify's API does not provide unrestricted access to a user's complete historical listening activity.

This project therefore works with the listening history and rankings made available through the API at the time of collection.

In particular:

- Recently played tracks are limited by Spotify's API.
- Top artist and track rankings represent Spotify's ranking data, not exact play counts.
- Track duration represents the full track length, not the amount of time actually listened to.
- The dataset does not contain skip rates or confirmed completion status.

These limitations are considered when interpreting the results.

## Database Design

PostgreSQL is used to organise the collected data into relational tables.

### Spotify tables

| Table | Description |
|---|---|
| `spotify_listeners` | Stores the Spotify listener profile |
| `spotify_artists` | Stores artist information |
| `spotify_tracks` | Stores track and album metadata |
| `spotify_track_artists` | Connects tracks with their associated artists |
| `spotify_streams` | Stores individual listening events and timestamps |
| `spotify_top_items` | Stores ranked top artists and tracks across different time ranges |

The database uses primary keys, foreign keys and unique constraints to maintain relationships and reduce duplicate records.

### SQL analysis

SQL queries are used to explore listening activity and music preferences.

Examples of planned analyses include:

- Total listening events
- Number of unique tracks played
- Most frequently played artists
- Most frequently played tracks
- Listening activity by date
- Listening patterns by hour
- Listening patterns by weekday
- Comparisons of top artists and tracks across Spotify time ranges

## Power BI Dashboard

Power BI is used to transform the database results into interactive visualisations.

The dashboard is organised into three sections.

### 1. My Music Identity

An overview of personal music preferences, including:

- Total listening events
- Unique tracks
- Most prominent artists
- Top tracks
- Spotify top-item rankings across different time ranges

### 2. When I Listen

An exploration of listening habits over time, including:

- Listening activity by date
- Listening activity by hour of the day
- Listening activity by weekday
- Recent listening events

### 3. My Music Taste Evolution

A comparison of Spotify's top artist and track rankings across:

- Short-term
- Medium-term
- Long-term

This section explores how music preferences differ across Spotify's ranking periods.

## Getting Started

### Prerequisites

Before running the project, install:

- Python 3.11 or later
- PostgreSQL
- Power BI Desktop
- Git
- A Spotify account
- A Spotify Developer application

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/music-taste-archaeology.git
cd music-taste-archaeology
```

### 2. Set up a Python virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a template.

Add your local PostgreSQL connection details and Spotify application configuration:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=music_archaeology
DB_USER=postgres
DB_PASSWORD=your_password

SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback

MAX_RECENT_PAGES=10
```

Do not commit your `.env` file or Spotify authentication tokens to GitHub.

### 5. Set up the PostgreSQL database

Create a PostgreSQL database named:

```sql
CREATE DATABASE music_archaeology;
```

Run the Spotify schema script:

```text
sql/04_create_spotify_tables.sql
```

This creates the tables needed to store Spotify data.

The earlier fictional dataset and its tables are separate from the Spotify dataset and can be used for SQL practice.

### 6. Configure Spotify Developer application

1. Visit the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).
2. Create a Spotify application.
3. Add the following redirect URI to the application settings:

   `http://127.0.0.1:8888/callback`

4. Copy the application Client ID into your `.env` file.

The importer uses PKCE authentication and does not require a client secret.

### 7. Import Spotify data

Run the importer from the project root:

```bash
python scripts/import_spotify.py
```

Follow the browser authentication instructions to authorise access to your Spotify account.

Once authenticated, the script retrieves the available listening history, top artists and top tracks, and inserts the results into PostgreSQL.

### 8. Analyse the data

Open the SQL scripts in the `sql/` directory to explore the database and run analytical queries.


## Future Improvements

Potential extensions to the project include:

- Automating periodic data collection.
- Tracking changes in top artist and track rankings over time.
- Adding genre-based analysis.
- Exploring artist diversity and music discovery patterns.
- Improving the dashboard with additional filters and drill-downs.
- Adding more advanced SQL queries and analytical measures.

## What I Learned

This project provides practical experience with:

- Retrieving and working with data from a REST API.
- Implementing OAuth 2.0 authentication with PKCE.
- Designing relational database schemas.
- Writing SQL queries for data exploration and analysis.
- Connecting Python applications to PostgreSQL.
- Preparing data for business intelligence reporting.
- Creating interactive dashboards in Power BI.
- Documenting and managing a data analytics project with Git and GitHub.

## Disclaimer

This is an independent personal project and is not affiliated with, endorsed by or sponsored by Spotify.

Spotify and its associated content remain the property of their respective owners.

Spotify-derived data is kept private and is not included in this public repository. Please review Spotify's current Developer Terms and Developer Policy before redistributing or publicly displaying Spotify-derived content.

---

**Author:** Zarin Maisha
**Project:** Music Taste Archaeology
