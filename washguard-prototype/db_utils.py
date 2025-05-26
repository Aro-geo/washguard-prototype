import sqlite3
from contextlib import contextmanager

@contextmanager
def db_connection():
    conn = sqlite3.connect("washguard.db")
    try:
        yield conn.cursor()
        conn.commit()
    finally:
        conn.close()
