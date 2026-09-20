"""SQLite connection and schema for the mini library."""

import os
import sqlite3
from collections.abc import Iterator
from pathlib import Path


def database_path() -> Path:
    configured = os.getenv("LIBRARY_DB_PATH")
    return Path(configured) if configured else Path(__file__).resolve().parent.parent / "library.db"


def connect() -> sqlite3.Connection:
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_db() -> Iterator[sqlite3.Connection]:
    connection = connect()
    try:
        yield connection
    finally:
        connection.close()


def create_schema() -> None:
    connection = connect()
    try:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS authors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK (length(trim(name)) > 0)
            );
            CREATE TABLE IF NOT EXISTS genres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK (length(trim(name)) > 0)
            );
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL CHECK (length(trim(title)) > 0),
                author_id INTEGER NOT NULL REFERENCES authors(id) ON DELETE RESTRICT,
                genre_id INTEGER NOT NULL REFERENCES genres(id) ON DELETE RESTRICT
            );
            CREATE TABLE IF NOT EXISTS readers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL CHECK (length(trim(name)) > 0),
                email TEXT NOT NULL CHECK (length(trim(email)) > 0)
            );
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id INTEGER NOT NULL REFERENCES books(id) ON DELETE RESTRICT,
                reader_id INTEGER NOT NULL REFERENCES readers(id) ON DELETE RESTRICT,
                loan_date TEXT NOT NULL CHECK (length(trim(loan_date)) > 0),
                returned INTEGER NOT NULL DEFAULT 0 CHECK (returned IN (0, 1))
            );
            """
        )
        connection.commit()
    finally:
        connection.close()
