import sqlite3
import bcrypt

DB_PATH = "suggestions.db"

def ensure_admin_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

def update_admin_password(username, new_password):
    ensure_admin_table()

    hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Ensure account exists
    cur.execute("SELECT id FROM admin WHERE username = ?;", (username,))
    row = cur.fetchone()

    if row is None:
        cur.execute(
            "INSERT INTO admin (username, password_hash) VALUES (?, ?);",
            (username, hashed)
        )
    else:
        cur.execute(
            "UPDATE admin SET password_hash = ? WHERE username = ?;",
            (hashed, username)
        )

    conn.commit()
    conn.close()
    print("Password updated successfully!")


# ----- RUN IT -----
update_admin_password("admin", "DenseThicketandMountainLaurel9?")