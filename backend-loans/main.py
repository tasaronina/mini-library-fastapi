import sqlite3
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI
from pydantic import BaseModel
from shared.database import create_tables, get_db
from shared.crud import get_rows, save_row, delete_row


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


@app.get("/health")
def health():
    return {"status": "ok"}


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
