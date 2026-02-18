import sqlite3
from backend.db import connect_db


def register(username, password):

    conn = connect_db()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO users VALUES (NULL, ?, ?)",
            (username, password)
        )
        conn.commit()
        return True

    except:
        return False

    finally:
        conn.close()


def login(username, password):

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    user = cur.fetchone()

    conn.close()

    return user is not None
