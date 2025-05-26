import sqlite3
from db_utils import db_connection

# Connect to the SQLite database
conn = sqlite3.connect("washguard.db")
cursor = conn.cursor()

# Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS chlorine (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tap_stand_id TEXT,
    date TEXT,
    time TEXT,
    chlorine_level REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS quality (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id TEXT,
    turbidity REAL,
    odour_present TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    household_id TEXT,
    feedback_text TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS infrastructure (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT,
    generator_ok TEXT,
    pump_ok TEXT,
    pipe_leak TEXT,
    road_condition TEXT,
    comments TEXT,
    water_available_liters INTEGER
)
""")

# Insert mock data only if tables are empty
def table_empty(cursor, table):
    cursor.execute(f"SELECT COUNT(*) FROM {table}")
    return cursor.fetchone()[0] == 0

if table_empty(cursor, "chlorine"):
    cursor.executemany("INSERT INTO chlorine (tap_stand_id, date, time, chlorine_level) VALUES (?, ?, ?, ?)", [
        ("TS-001", "2025-05-21", "08:30:00", 0.15),
        ("TS-002", "2025-05-22", "09:00:00", 0.35),
        ("TS-003", "2025-05-23", "09:30:00", 0.60),
    ])   

if table_empty(cursor, "quality"):
    cursor.executemany("INSERT INTO quality (source_id, turbidity, odour_present) VALUES (?, ?, ?)", [
        ("Source-A", 3.5, "No"),
        ("Source-B", 6.0, "Yes"),
        ("Source-C", 2.2, "No"),
    ])   

if table_empty(cursor, "feedback"):
    cursor.executemany("INSERT INTO feedback (household_id, feedback_text) VALUES (?, ?)", [
        ("HH-001", "Water pressure is too low."),
        ("HH-002", "We are happy with the clean water."),
        ("HH-003", "Please fix the broken tap."),
        ("HH-004", "The water quality has improved this week, thank you."),
    ])   

if table_empty(cursor, "infrastructure"):
    cursor.executemany("""
        INSERT INTO infrastructure (location, generator_ok, pump_ok, pipe_leak, road_condition, comments, water_available_liters)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        ("Zone A", "Yes", "Yes", "No", "Good", "All systems go", 800),
        ("Zone B", "No", "Yes", "Yes", "Flooded", "Generator failure and pipe leak", 400),
        ("Zone E", "Yes", "Yes", "Yes", "Moderate", "Small pipe leak detected, team dispatched", 12),
    ])

# Commit changes and close
conn.commit()
conn.close()

def get_all_chlorine():
    with db_connection() as cursor:
        cursor.execute("SELECT tap_stand_id, date, time, chlorine_level FROM chlorine")
        return cursor.fetchall()

def insert_chlorine(tap_stand_id, date, time, chlorine_level):
    with db_connection() as cursor:
        cursor.execute(
            "INSERT INTO chlorine (tap_stand_id, date, time, chlorine_level) VALUES (?, ?, ?, ?)",
            (tap_stand_id, date, time, chlorine_level)
        )

def get_all_quality():
    with db_connection() as cursor:
        cursor.execute("SELECT source_id, turbidity, odour_present FROM quality")
        return cursor.fetchall()

def insert_quality(source_id, turbidity, odour_present):
    with db_connection() as cursor:
        cursor.execute(
            "INSERT INTO quality (source_id, turbidity, odour_present) VALUES (?, ?, ?)",
            (source_id, turbidity, odour_present)
        )

def get_all_feedback():
    with db_connection() as cursor:
        cursor.execute("SELECT household_id, feedback_text FROM feedback")
        return cursor.fetchall()

def insert_feedback(household_id, feedback_text):
    with db_connection() as cursor:
        cursor.execute(
            "INSERT INTO feedback (household_id, feedback_text) VALUES (?, ?)",
            (household_id, feedback_text)
        )

def get_all_infrastructure():
    with db_connection() as cursor:
        cursor.execute("SELECT location, generator_ok, pump_ok, pipe_leak, road_condition, comments, water_available_liters FROM infrastructure")
        return cursor.fetchall()

def insert_infrastructure(location, generator_ok, pump_ok, pipe_leak, road_condition, comments, water_available_liters):
    with db_connection() as cursor:
        cursor.execute(
            "INSERT INTO infrastructure (location, generator_ok, pump_ok, pipe_leak, road_condition, comments, water_available_liters) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (location, generator_ok, pump_ok, pipe_leak, road_condition, comments, water_available_liters)
        )
