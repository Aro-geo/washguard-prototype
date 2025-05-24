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
    ("TS-001", "2025-05-21", "08:30:00", 0.15),
    ("TS-002", "2025-05-21", "09:00:00", 0.35),
    ("TS-003", "2025-05-21", "09:30:00", 0.60),
    ("TS-004", "2025-05-21", "09:45:00", 0.32),
    ("TS-005", "2025-05-21", "10:00:00", 0.41),
    ("TS-006", "2025-05-21", "10:15:00", 0.19),
])

cursor.executemany("INSERT INTO quality (source_id, turbidity, odour_present) VALUES (?, ?, ?)", [
    ("Source-A", 3.5, "No"),
    ("Source-B", 6.0, "Yes"),
    ("Source-C", 2.2, "No"),
    ("Source-D", 2.1, "No"),
    ("Source-E", 8.4, "Yes"),
])

cursor.executemany("INSERT INTO feedback (household_id, feedback_text) VALUES (?, ?)", [
    ("HH-001", "Water pressure is too low."),
    ("HH-002", "We are happy with the clean water."),
    ("HH-003", "Please fix the broken tap."),
    ("HH-004", "The water quality has improved this week, thank you."),
    ("HH-005", "Pump is working fine now after repairs."),
    ("HH-006", "We need more water purification tablets urgently."),
    ("HH-007", "Distributing water to elderly is challenging due to the distance."),
])

cursor.executemany("""
    INSERT INTO infrastructure (location, generator_ok, pump_ok, pipe_leak, road_condition, comments, water_available_liters)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""", [
    ("Zone A", "Yes", "Yes", "No", "Good", "All systems go", 800),
    ("Zone B", "No", "Yes", "Yes", "Flooded", "Generator failure and pipe leak", 400),
    ("Zone C", "Yes", "No", "No", "Muddy", "Pump broken down", 300),
    ("Zone D", "Yes", "Yes", "No", "Good", "Regular maintenance scheduled", 15),
    ("Zone E", "Yes", "Yes", "Yes", "Moderate", "Small pipe leak detected, team dispatched", 12),
])

# Commit changes and close
conn.commit()
conn.close()

def get_all_chlorine():
    conn = sqlite3.connect("washguard.db")
    cursor = conn.cursor()
    cursor.execute("SELECT tap_stand_id, date, time, chlorine_level FROM chlorine")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_quality():
    conn = sqlite3.connect("washguard.db")
    cursor = conn.cursor()
    cursor.execute("SELECT source_id, turbidity, odour_present FROM quality")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_feedback():
    conn = sqlite3.connect("washguard.db")
    cursor = conn.cursor()
    cursor.execute("SELECT household_id, feedback_text FROM feedback")
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_all_infrastructure():
    conn = sqlite3.connect("washguard.db")
    cursor = conn.cursor()
    cursor.execute("SELECT location, generator_ok, pump_ok, pipe_leak, road_condition, comments, water_available_liters FROM infrastructure")
    rows = cursor.fetchall()
    conn.close()
    return rows

def insert_feedback(household_id, feedback_text):
    conn = sqlite3.connect("washguard.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO feedback (household_id, feedback_text) VALUES (?, ?)", (household_id, feedback_text))
    conn.commit()
    conn.close()

def insert_chlorine(tap_stand_id, date, time, chlorine_level):
    conn = sqlite3.connect("washguard.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO chlorine (tap_stand_id, date, time, chlorine_level) VALUES (?, ?, ?, ?)",
        (tap_stand_id, date, time, chlorine_level)
    )
    conn.commit()
    conn.close()

def insert_quality(source_id, turbidity, odour_present):
    conn = sqlite3.connect("washguard.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO quality (source_id, turbidity, odour_present) VALUES (?, ?, ?)",
        (source_id, turbidity, odour_present)
    )
    conn.commit()
    conn.close()

def insert_infrastructure(location, generator_ok, pump_ok, pipe_leak, road_condition, comments, water_available_liters):
    conn = sqlite3.connect("washguard.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO infrastructure (location, generator_ok, pump_ok, pipe_leak, road_condition, comments, water_available_liters) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (location, generator_ok, pump_ok, pipe_leak, road_condition, comments, water_available_liters)
    )
    conn.commit()
    conn.close()
