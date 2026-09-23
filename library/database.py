import sqlite3
from collections.abc import Iterator
from pathlib import Path


DB_FILE = Path(__file__).resolve().parent.parent / "library.db"


def connect():
    db = sqlite3.connect(DB_FILE, check_same_thread=False)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def get_db() -> Iterator[sqlite3.Connection]:
    db = connect()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    db = connect()
    db.executescript(
        """
        CREATE TABLE IF NOT EXISTS authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS genres (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author_id INTEGER NOT NULL REFERENCES authors(id),
            genre_id INTEGER NOT NULL REFERENCES genres(id)
        );
        CREATE TABLE IF NOT EXISTS readers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS loans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL REFERENCES books(id),
            reader_id INTEGER NOT NULL REFERENCES readers(id),
            loan_date TEXT NOT NULL,
            returned INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    db.commit()
    db.close()
