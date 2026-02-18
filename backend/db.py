import sqlite3


import os

DB_NAME = os.path.join("/tmp", "users.db")


def connect_db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():

    conn = connect_db()
    cur = conn.cursor()

    # Users
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Chats
    cur.execute("""
    CREATE TABLE IF NOT EXISTS chats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        question TEXT,
        answer TEXT
    )
    """)

    conn.commit()
    conn.close()
def save_chat(username, question, answer):

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO chats VALUES (NULL, ?, ?, ?)",
        (username, question, answer)
    )

    conn.commit()
    conn.close()


def load_chats(username):

    conn = connect_db()
    cur = conn.cursor()

    cur.execute(
        "SELECT question, answer FROM chats WHERE username=?",
        (username,)
    )

    rows = cur.fetchall()

    conn.close()

    return rows
