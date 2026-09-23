import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .database import create_tables, get_db


class Author(BaseModel):
    name: str


class Genre(BaseModel):
    name: str


class Book(BaseModel):
    title: str
    author_id: int
    genre_id: int


class Reader(BaseModel):
    name: str
    email: str


class Loan(BaseModel):
    book_id: int
    reader_id: int
    loan_date: str
    returned: bool = False


Db = Annotated[sqlite3.Connection, Depends(get_db)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(lifespan=lifespan)
static = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static), name="static")


@app.get("/", include_in_schema=False)
def home():
    return FileResponse(static / "index.html")


def get_rows(db, table):
    return [dict(row) for row in db.execute(f"SELECT * FROM {table} ORDER BY id")]


def get_row(db, table, item_id):
    row = db.execute(f"SELECT * FROM {table} WHERE id = ?", (item_id,)).fetchone()
    if row is None:
        raise HTTPException(404, "Запись не найдена")
    return dict(row)


def save_row(db, table, data, item_id=None):
    columns = list(data)
    values = list(data.values())
    try:
        if item_id is None:
            marks = ", ".join("?" for column in columns)
            cursor = db.execute(
                f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({marks})",
                values,
            )
            item_id = cursor.lastrowid
        else:
            get_row(db, table, item_id)
            fields = ", ".join(f"{column} = ?" for column in columns)
            db.execute(f"UPDATE {table} SET {fields} WHERE id = ?", [*values, item_id])
        db.commit()
        return get_row(db, table, item_id)
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Проверьте данные")


def delete_row(db, table, item_id):
    get_row(db, table, item_id)
    try:
        db.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))
        db.commit()
        return Response(status_code=204)
    except sqlite3.IntegrityError:
        raise HTTPException(409, "Запись используется")


@app.get("/api/authors")
def authors(db: Db):
    return get_rows(db, "authors")


@app.post("/api/authors")
def add_author(data: Author, db: Db):
    return save_row(db, "authors", data.model_dump())


@app.put("/api/authors/{item_id}")
def edit_author(item_id: int, data: Author, db: Db):
    return save_row(db, "authors", data.model_dump(), item_id)


@app.delete("/api/authors/{item_id}")
def remove_author(item_id: int, db: Db):
    return delete_row(db, "authors", item_id)


@app.get("/api/genres")
def genres(db: Db):
    return get_rows(db, "genres")


@app.post("/api/genres")
def add_genre(data: Genre, db: Db):
    return save_row(db, "genres", data.model_dump())


@app.put("/api/genres/{item_id}")
def edit_genre(item_id: int, data: Genre, db: Db):
    return save_row(db, "genres", data.model_dump(), item_id)


@app.delete("/api/genres/{item_id}")
def remove_genre(item_id: int, db: Db):
    return delete_row(db, "genres", item_id)


@app.get("/api/books")
def books(db: Db):
    return get_rows(db, "books")


@app.post("/api/books")
def add_book(data: Book, db: Db):
    return save_row(db, "books", data.model_dump())


@app.put("/api/books/{item_id}")
def edit_book(item_id: int, data: Book, db: Db):
    return save_row(db, "books", data.model_dump(), item_id)


@app.delete("/api/books/{item_id}")
def remove_book(item_id: int, db: Db):
    return delete_row(db, "books", item_id)


@app.get("/api/readers")
def readers(db: Db):
    return get_rows(db, "readers")


@app.post("/api/readers")
def add_reader(data: Reader, db: Db):
    return save_row(db, "readers", data.model_dump())


@app.put("/api/readers/{item_id}")
def edit_reader(item_id: int, data: Reader, db: Db):
    return save_row(db, "readers", data.model_dump(), item_id)


@app.delete("/api/readers/{item_id}")
def remove_reader(item_id: int, db: Db):
    return delete_row(db, "readers", item_id)


@app.get("/api/loans")
def loans(db: Db):
    return get_rows(db, "loans")


@app.post("/api/loans")
def add_loan(data: Loan, db: Db):
    return save_row(db, "loans", data.model_dump())


@app.put("/api/loans/{item_id}")
def edit_loan(item_id: int, data: Loan, db: Db):
    return save_row(db, "loans", data.model_dump(), item_id)


@app.delete("/api/loans/{item_id}")
def remove_loan(item_id: int, db: Db):
    return delete_row(db, "loans", item_id)
