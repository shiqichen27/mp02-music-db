"""
tests.py
==========
CIS 3120 · MP02 — SQL and Database
Author 3 module — test cases
"""

import sqlite3
import unittest
from schema_data import build_database, seed_database
from queries import get_playlist_tracks, get_tracks_on_no_playlist, get_most_added_track, get_playlist_durations

# ─────────────────────────────────────────────────────────────────────────────
# Class 1 — Testing Schema Data
# ─────────────────────────────────────────────────────────────────────────────

class TestSchema(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON;")
        build_database(self.conn)

    def tearDown(self):
        self.conn.close()

    def test_tables_exist(self): 
    # checks that one table name exists in the list
        cursor = self.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        self.assertIn("Artist", tables)
        self.assertIn("Track", tables)
        self.assertIn("Playlist", tables)
        self.assertIn("PlaylistTrack", tables)

    def test_track_rejects_invalid_artist(self): 
        ''' tests the foreign key contstraint on Track.artist_id by inserting a track 
        referencing an artist id that doesn't exist '''
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute(
                '''INSERT INTO Track (track_id, title, duration_seconds, artist_id)
                VALUES (9999, 'Ghost Track', 210, 9999)'''
            )

# ─────────────────────────────────────────────────────────────────────────────
# Class 2 — Testing Seed Data
# ─────────────────────────────────────────────────────────────────────────────

class TestSeedData(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON;")
        build_database(self.conn) 
        seed_database(self.conn)

    def tearDown(self):
        self.conn.close()
    
    def test_artist_count(self): 
    # counts the rows in Artist and ensures it's at least 6
        count = self.conn.execute("SELECT COUNT(*) FROM Artist").fetchone()[0]
        self.assertGreaterEqual(count, 6)
    
    def test_track_count(self): 
    # counts the rows in Track and ensures it's at least 18
        count = self.conn.execute("SELECT COUNT(*) FROM Track").fetchone()[0]
        self.assertGreaterEqual(count, 18)

    def test_playlist_count(self): 
    # counts the rows in Playlist and ensures it's at least 4
        count = self.conn.execute("SELECT COUNT(*) FROM Playlist").fetchone()[0]
        self.assertGreaterEqual(count, 4)

    def test_playlisttrack_count(self):
    # counts the rows in PlaylistTrack and ensures it's at least 20
        count = self.conn.execute("SELECT COUNT(*) FROM PlaylistTrack").fetchone()[0]
        self.assertGreaterEqual(count, 20)

# ─────────────────────────────────────────────────────────────────────────────
# Class 3 — Testing Queries
# ─────────────────────────────────────────────────────────────────────────────

class TestQueries(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON;")
        build_database(self.conn) 
        seed_database(self.conn)
        self.playlist_name = self.conn.execute("SELECT playlist_name FROM Playlist LIMIT 1").fetchone()[0]
        # takes the name of the first playlist and stores it as self.playlist_name

    def tearDown(self):
        self.conn.close()

    def test_get_playlist_tracks(self):
    # asserts at least one row is returned, indicating JOIN worked
        rows = get_playlist_tracks(self.conn, self.playlist_name)
        self.assertGreater(len(rows), 0)

    def test_get_tracks_on_no_playlist(self):
    # checks if the function ran without error by checking that the return type is a list
        result = get_tracks_on_no_playlist(self.conn)
        self.assertIsInstance(result, list)

    def test_get_most_added_track(self):
    # asserts that only one row is returned because we are looking for the most added track (one result)
        result = get_most_added_track(self.conn)
        self.assertEqual(len(result), 1)

    def test_get_playlist_durations(self):
    # checks that the return type is a list
        result = get_playlist_durations(self.conn)
        self.assertIsInstance(result, list)

# ─────────────────────────────────────────────────────────────────────────────
# Class 4 — Testing Deletion Cases
# ─────────────────────────────────────────────────────────────────────────────

class TestDeletions(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.conn.execute("PRAGMA foreign_keys = ON;")
        build_database(self.conn) 
        seed_database(self.conn)
        self.artist_id = self.conn.execute("SELECT artist_id FROM Artist LIMIT 1").fetchone()[0]

    def tearDown(self):
        self.conn.close()

    def test_deletion_removes_artist(self):
    # tests that the 3-step deletion removes the artist from the database
        self.conn.execute( # deletes all PlaylistTrack rows that reference any of the selected artist's tracks
            "DELETE FROM PlaylistTrack WHERE track_id IN "
            "(SELECT track_id FROM Track WHERE artist_id = ?)", (self.artist_id,)
        )
        self.conn.execute("DELETE FROM Track WHERE artist_id = ?", (self.artist_id,)) # deletes artist's tracks from Track 
        self.conn.execute("DELETE FROM Artist WHERE artist_id = ?", (self.artist_id,)) # deletes artist row
        self.conn.commit()

        row = self.conn.execute("SELECT artist_id FROM Artist WHERE artist_id = ?", (self.artist_id,)).fetchone()
        self.assertIsNone(row) # confirms artist was deleted

    def test_wrong_deletion_order_raises_error(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.conn.execute("DELETE FROM Track WHERE artist_id = ?", (self.artist_id,))
    

if __name__ == "__main__":
    unittest.main(verbosity=2)
    