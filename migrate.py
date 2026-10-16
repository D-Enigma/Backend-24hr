import sqlite3

# Connect to the existing database to update its table structure.
conn = sqlite3.connect("complaints.db")
cur = conn.cursor()

# Check which columns already exist in the complaints table.
cur.execute("PRAGMA table_info(complaints)")
columns = [col[1] for col in cur.fetchall()]

# Add user_id only if it isn't already there, so the migration can be rerun safely.
if "user_id" not in columns:
    cur.execute(
        "ALTER TABLE complaints ADD COLUMN user_id INTEGER REFERENCES users(id)"
    )
    conn.commit()
    print("Migration successful: user_id added.")
else:
    print("Migration skipped: user_id already exists.")

# Close the database connection after the migration is complete.
conn.close()
