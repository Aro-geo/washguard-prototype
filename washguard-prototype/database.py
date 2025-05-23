import sqlite3
import os

DB_FILE = "wash.db"

# Ensure DB exists
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create tables if they don't exist
def create_tables_if_not_exist():
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chlorine (
        tap_stand_id TEXT,
        date TEXT,
        time TEXT,
        chlorine_level REAL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS quality (
        source_id TEXT,
        turbidity REAL,
        odour_present TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        household_id TEXT,
        feedback_text TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS infrastructure (
        location TEXT,
        generator_ok TEXT,
        pump_ok TEXT,
        pipe_leak TEXT,
        road_condition TEXT,
        comments TEXT,
        water_available_liters INTEGER
    )
    """)
    conn.commit()

# Check if a table is empty
def is_table_empty(table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    return count == 0

# Insert mock data (only if DB is empty)
def insert_mock_data():
    cursor.executemany("""
    INSERT INTO chlorine (tap_stand_id, date, time, chlorine_level) VALUES (?, ?, ?, ?)
    """, [
        ("TS-001", "2025-05-22", "09:00", 0.18),
        ("TS-002", "2025-05-22", "09:10", 0.26),
        ("TS-003", "2025-05-22", "09:15", 0.55),
    ])

    cursor.executemany("""
    INSERT INTO quality (source_id, turbidity, odour_present) VALUES (?, ?, ?)
    """, [
        ("WS-001", 7.2, "Yes"),
        ("WS-002", 3.0, "No")
    ])

    cursor.executemany("""
    INSERT INTO feedback (household_id, feedback_text) VALUES (?, ?)
    """, [
        ("HH-001", "Water smells bad and no soap in stock"),
        ("HH-002", "Latrine is clean, but chlorine taste is strong"),
        ("HH-003", "Kids complain about dirty water and no aqua tabs")
    ])

    cursor.executemany("""
    INSERT INTO infrastructure (location, generator_ok, pump_ok, pipe_leak, road_condition, comments, water_available_liters) VALUES (?, ?, ?, ?, ?, ?, ?)
    """, [
        ("Zone A", "Yes", "Yes", "No", "Good", "All systems functional", 20),
        ("Zone B", "No", "Yes", "Yes", "Muddy", "Generator won't start, needs oil", 5),
        ("Zone C", "Yes", "No", "No", "Flooded", "Pump pressure low, maybe blockage", 8)
    ])

    conn.commit()

# Execute table creation
create_tables_if_not_exist()

# Load mock data only if all tables are empty
if all([
    is_table_empty("chlorine"),
    is_table_empty("quality"),
    is_table_empty("feedback"),
    is_table_empty("infrastructure")
]):
    insert_mock_data()

conn.close()

# Insert functions
def insert_chlorine(tap_stand_id, date, time, chlorine_level):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO chlorine (tap_stand_id, date, time, chlorine_level)
            VALUES (?, ?, ?, ?)
        """, (tap_stand_id, date, time, chlorine_level))
        conn.commit()
        print(f"✅ Inserted chlorine for {tap_stand_id}")
    except Exception as e:
        print("❌ Chlorine insert failed:", e)
    finally:
        conn.close()

def get_all_chlorine():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chlorine")
    data = cursor.fetchall()
    conn.close()
    return data

def insert_quality(source_id, turbidity, odour_present):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO quality (source_id, turbidity, odour_present)
            VALUES (?, ?, ?)
        """, (source_id, turbidity, odour_present))
        conn.commit()
        print(f"✅ Inserted quality for {source_id}")
    except Exception as e:
        print("❌ Quality insert failed:", e)
    finally:
        conn.close()

def get_all_quality():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quality")
    data = cursor.fetchall()
    conn.close()
    return data

def insert_feedback(household_id, feedback_text):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO feedback (household_id, feedback_text)
            VALUES (?, ?)
        """, (household_id, feedback_text))
        conn.commit()
        print(f"✅ Inserted feedback for {household_id}")
    except Exception as e:
        print("❌ Feedback insert failed:", e)
    finally:
        conn.close()

def get_all_feedback():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM feedback")
    data = cursor.fetchall()
    conn.close()
    return data

def insert_infrastructure(location, generator_ok, pump_ok, pipe_leak, road_condition, comments, water_available_liters):
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO infrastructure (
                location, generator_ok, pump_ok, pipe_leak,
                road_condition, comments, water_available_liters
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (location, generator_ok, pump_ok, pipe_leak,
              road_condition, comments, water_available_liters))
        conn.commit()
        print(f"✅ Inserted infrastructure for {location}")
    except Exception as e:
        print("❌ Infrastructure insert failed:", e)
    finally:
        conn.close()

def get_all_infrastructure():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM infrastructure")
    data = cursor.fetchall()
    conn.close()
    return data
