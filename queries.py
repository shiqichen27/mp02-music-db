import sqlite3

def get_playlist_tracks(conn, playlist_name):
    """Return all tracks on the named playlist, ordered by position."""
    query = """
        SELECT  t.title,
                a.name AS artist_name,
                t.duration_seconds,
                pt.position
        FROM    PlaylistTrack pt
        JOIN    Track    t  ON pt.track_id    = t.track_id
        JOIN    Artist   a  ON t.artist_id    = a.artist_id
        JOIN    Playlist p  ON pt.playlist_id = p.playlist_id
        WHERE   p.playlist_name = ?
        ORDER BY pt.position ASC
    """
    return conn.execute(query, (playlist_name,)).fetchall()


def get_tracks_on_no_playlist(conn):
    """Return all tracks that do not appear on any playlist."""
    query = """
        SELECT  t.track_id,
                t.title,
                a.name AS artist_name
        FROM    Track t
        JOIN    Artist a ON t.artist_id = a.artist_id
        LEFT JOIN PlaylistTrack pt ON t.track_id = pt.track_id
        WHERE   pt.track_id IS NULL
    """
    return conn.execute(query).fetchall()


def get_most_added_track(conn):
    """Return the track appearing on the greatest number of playlists."""
    query = """
        SELECT  t.title,
                a.name AS artist_name,
                COUNT(*) AS playlist_count
        FROM    PlaylistTrack pt
        JOIN    Track  t ON pt.track_id  = t.track_id
        JOIN    Artist a ON t.artist_id  = a.artist_id
        GROUP BY pt.track_id
        ORDER BY playlist_count DESC
        LIMIT 1
    """
    return conn.execute(query).fetchall()


def get_playlist_durations(conn):
    """Return each playlist name and total duration in minutes, descending."""
    query = """
        SELECT  p.playlist_name,
                SUM(t.duration_seconds) / 60.0 AS total_minutes
        FROM    PlaylistTrack pt
        JOIN    Track    t ON pt.track_id    = t.track_id
        JOIN    Playlist p ON pt.playlist_id = p.playlist_id
        GROUP BY pt.playlist_id
        ORDER BY total_minutes DESC
    """
    return conn.execute(query).fetchall()