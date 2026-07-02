import sqlite3

conn = sqlite3.connect("third_eye.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS faces(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gender TEXT,
    age TEXT,
    face TEXT,
    hair TEXT,
    eyes TEXT,
    skin TEXT,
    description TEXT,
    image TEXT
)
""")

conn.commit()
conn.close()

print("Database Created Successfully")