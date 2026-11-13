"""Проверяем микросервисы: доступность и прежние операции с базой."""
import importlib.util
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "backend-shared") not in sys.path:
    sys.path.insert(0, str(ROOT / "backend-shared"))
# On the host the original directory is named backend-shared; inside Docker it is shared.
# Reuse the same shared module object for both FastAPI apps.
if "shared" not in sys.modules:
    spec = importlib.util.spec_from_file_location(
        "shared", ROOT / "backend-shared" / "__init__.py",
        submodule_search_locations=[str(ROOT / "backend-shared")],
    )
    shared = importlib.util.module_from_spec(spec)
    sys.modules["shared"] = shared
    spec.loader.exec_module(shared)


def import_service(name):
    spec = importlib.util.spec_from_file_location(
        f"test_{name}_service", ROOT / f"backend-{name}" / "main.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.app


catalog = import_service("catalog")
loans = import_service("loans")
from shared import database  # noqa: E402


@pytest.fixture
def clients(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", tmp_path / "library.db")
    with TestClient(catalog) as cat, TestClient(loans) as loan:
        yield cat, loan


def test_health(clients):
    cat, loan = clients
    assert cat.get("/health").json() == {"status": "ok"}
    assert loan.get("/health").json() == {"status": "ok"}


def test_catalog_and_loans_share_db(clients):
    cat, loan = clients
    author = cat.post("/api/authors", json={"name": "Автор"}).json()
    genre = cat.post("/api/genres", json={"name": "Жанр"}).json()
    book_response = cat.post("/api/books", json={
        "title": "Книга", "author_id": author["id"], "genre_id": genre["id"]
    })
    assert book_response.status_code == 200
    book = book_response.json()
    reader = loan.post("/api/readers", json={
        "name": "Читатель", "email": "reader@example.com"
    }).json()
    issued = loan.post("/api/loans", json={
        "book_id": book["id"], "reader_id": reader["id"], "loan_date": "2026-11-12"
    })
    assert issued.status_code == 200
    assert issued.json()["book_id"] == book["id"]
