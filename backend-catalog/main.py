import sqlite3
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from shared.database import create_tables, get_db
from shared.crud import get_rows, save_row, delete_row


class Author(BaseModel):
    name: str


class Genre(BaseModel):
    name: str


class Book(BaseModel):
    title: str
    author_id: int
    genre_id: int


Db = Annotated[sqlite3.Connection, Depends(get_db)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "ok"}


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
