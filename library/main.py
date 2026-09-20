"""Five resources with complete CRUD and a tiny browser client."""

import sqlite3
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .database import create_schema, get_db


class AuthorIn(BaseModel):
    name: str = Field(min_length=1)


class GenreIn(BaseModel):
    name: str = Field(min_length=1)


class BookIn(BaseModel):
    title: str = Field(min_length=1)
    author_id: int = Field(gt=0)
    genre_id: int = Field(gt=0)


class ReaderIn(BaseModel):
    name: str = Field(min_length=1)
    email: str = Field(min_length=1)


class LoanIn(BaseModel):
    book_id: int = Field(gt=0)
    reader_id: int = Field(gt=0)
    loan_date: date
    returned: bool = False


Db = Annotated[sqlite3.Connection, Depends(get_db)]


@asynccontextmanager
async def lifespan(_app: FastAPI):
    create_schema()
    yield


app = FastAPI(title="Мини-библиотека", lifespan=lifespan)
static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", include_in_schema=False)
def homepage():
    return FileResponse(static_dir / "index.html")


def rows(db: sqlite3.Connection, table: str) -> list[dict]:
    return [dict(row) for row in db.execute(f"SELECT * FROM {table} ORDER BY id")]


def row_or_404(db: sqlite3.Connection, table: str, item_id: int) -> dict:
    item = db.execute(f"SELECT * FROM {table} WHERE id = ?", (item_id,)).fetchone()
    if item is None:
        raise HTTPException(status_code=404, detail="Запись не найдена")
    return dict(item)


def save(db: sqlite3.Connection, table: str, values: dict, item_id: int | None = None) -> dict:
    # Table names and column names below come only from our fixed models, never from a request.
    columns = list(values)
    parameters = list(values.values())
    try:
        if item_id is None:
            placeholders = ", ".join("?" for _ in columns)
            cursor = db.execute(
                f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
                parameters,
            )
            item_id = cursor.lastrowid
        else:
            row_or_404(db, table, item_id)
            assignments = ", ".join(f"{column} = ?" for column in columns)
            db.execute(
                f"UPDATE {table} SET {assignments} WHERE id = ?",
                [*parameters, item_id],
            )
        db.commit()
    except sqlite3.IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Проверьте поля и связанные записи") from exc
    return row_or_404(db, table, item_id)


def delete(db: sqlite3.Connection, table: str, item_id: int) -> Response:
    row_or_404(db, table, item_id)
    try:
        db.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))
        db.commit()
    except sqlite3.IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Сначала удалите связанные записи") from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# Authors: five HTTP operations.
@app.get("/api/authors")
def list_authors(db: Db):
    return rows(db, "authors")


@app.get("/api/authors/{item_id}")
def get_author(item_id: int, db: Db):
    return row_or_404(db, "authors", item_id)


@app.post("/api/authors", status_code=201)
def create_author(data: AuthorIn, db: Db):
    return save(db, "authors", data.model_dump())


@app.put("/api/authors/{item_id}")
def update_author(item_id: int, data: AuthorIn, db: Db):
    return save(db, "authors", data.model_dump(), item_id)


@app.delete("/api/authors/{item_id}", status_code=204)
def delete_author(item_id: int, db: Db):
    return delete(db, "authors", item_id)


# Genres: five HTTP operations.
@app.get("/api/genres")
def list_genres(db: Db):
    return rows(db, "genres")


@app.get("/api/genres/{item_id}")
def get_genre(item_id: int, db: Db):
    return row_or_404(db, "genres", item_id)


@app.post("/api/genres", status_code=201)
def create_genre(data: GenreIn, db: Db):
    return save(db, "genres", data.model_dump())


@app.put("/api/genres/{item_id}")
def update_genre(item_id: int, data: GenreIn, db: Db):
    return save(db, "genres", data.model_dump(), item_id)


@app.delete("/api/genres/{item_id}", status_code=204)
def delete_genre(item_id: int, db: Db):
    return delete(db, "genres", item_id)


# Books: five HTTP operations.
@app.get("/api/books")
def list_books(db: Db):
    return rows(db, "books")


@app.get("/api/books/{item_id}")
def get_book(item_id: int, db: Db):
    return row_or_404(db, "books", item_id)


@app.post("/api/books", status_code=201)
def create_book(data: BookIn, db: Db):
    return save(db, "books", data.model_dump())


@app.put("/api/books/{item_id}")
def update_book(item_id: int, data: BookIn, db: Db):
    return save(db, "books", data.model_dump(), item_id)


@app.delete("/api/books/{item_id}", status_code=204)
def delete_book(item_id: int, db: Db):
    return delete(db, "books", item_id)


# Readers: five HTTP operations.
@app.get("/api/readers")
def list_readers(db: Db):
    return rows(db, "readers")


@app.get("/api/readers/{item_id}")
def get_reader(item_id: int, db: Db):
    return row_or_404(db, "readers", item_id)


@app.post("/api/readers", status_code=201)
def create_reader(data: ReaderIn, db: Db):
    return save(db, "readers", data.model_dump())


@app.put("/api/readers/{item_id}")
def update_reader(item_id: int, data: ReaderIn, db: Db):
    return save(db, "readers", data.model_dump(), item_id)


@app.delete("/api/readers/{item_id}", status_code=204)
def delete_reader(item_id: int, db: Db):
    return delete(db, "readers", item_id)


# Loans: five HTTP operations.
@app.get("/api/loans")
def list_loans(db: Db):
    return rows(db, "loans")


@app.get("/api/loans/{item_id}")
def get_loan(item_id: int, db: Db):
    return row_or_404(db, "loans", item_id)


@app.post("/api/loans", status_code=201)
def create_loan(data: LoanIn, db: Db):
    return save(db, "loans", data.model_dump(mode="json"))


@app.put("/api/loans/{item_id}")
def update_loan(item_id: int, data: LoanIn, db: Db):
    return save(db, "loans", data.model_dump(mode="json"), item_id)


@app.delete("/api/loans/{item_id}", status_code=204)
def delete_loan(item_id: int, db: Db):
    return delete(db, "loans", item_id)
