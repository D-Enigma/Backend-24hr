import sqlite3

conn = sqlite3.connect("complaints.db")
cur = conn.cursor()

cur.execute("PRAGMA table_info(complaints)")
columns = [col[1] for col in cur.fetchall()]

if "user_id" not in columns:
    cur.execute(
        "ALTER TABLE complaints ADD COLUMN user_id INTEGER REFERENCES users(id)"
    )
    conn.commit()
    print("Migration successful: user_id added.")
else:
    print("Migration skipped: user_id already exists.")

conn.close()
