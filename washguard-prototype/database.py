import sqlite3

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

# Insert mock data
cursor.executemany("INSERT INTO chlorine (tap_stand_id, date, time, chlorine_level) VALUES (?, ?, ?, ?)", [
    ("Tap-001", "2025-05-21", "08:30:00", 0.15),
    ("Tap-002", "2025-05-21", "09:00:00", 0.35),
    ("Tap-003", "2025-05-21", "09:30:00", 0.60),
])

cursor.executemany("INSERT INTO quality (source_id, turbidity, odour_present) VALUES (?, ?, ?)", [
    ("Source-A", 3.5, "No"),
    ("Source-B", 6.0, "Yes"),
    ("Source-C", 2.2, "No"),
])

cursor.executemany("INSERT INTO feedback (household_id, feedback_text) VALUES (?, ?)", [
    ("HH-001", "Water pressure is too low."),
    ("HH-002", "We are happy with the clean water."),
    ("HH-003", "Please fix the broken tap."),
])

cursor.executemany("""
    INSERT INTO infrastructure (location, generator_ok, pump_ok, pipe_leak, road_condition, comments, water_available_liters)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", [
    ("Zone A", "Yes", "Yes", "No", "Good", "All systems go", 800),
    ("Zone B", "No", "Yes", "Yes", "Flooded", "Generator failure and pipe leak", 400),
    ("Zone C", "Yes", "No", "No", "Muddy", "Pump broken down", 300),
])

# Commit changes and close
conn.commit()
conn.close()
