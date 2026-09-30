import pytest
from fastapi.testclient import TestClient

from library import database
from library.main import app


RESOURCES = ("authors", "genres", "books", "readers", "loans")


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_FILE", tmp_path / "test.db")
    with TestClient(app) as test_client:
        yield test_client


def payload(client, resource, changed=False):
    if resource == "authors":
        return {"name": "Новый автор" if changed else "Автор"}
    if resource == "genres":
        return {"name": "Новый жанр" if changed else "Жанр"}
    if resource == "readers":
        return {
            "name": "Новый читатель" if changed else "Читатель",
            "email": "reader@example.com",
        }
    if resource == "books":
        author = client.post("/api/authors", json={"name": "Автор"}).json()
        genre = client.post("/api/genres", json={"name": "Жанр"}).json()
        return {
            "title": "Новая книга" if changed else "Книга",
            "author_id": author["id"],
            "genre_id": genre["id"],
        }
    book = client.post("/api/books", json=payload(client, "books")).json()
    reader = client.post(
        "/api/readers",
        json={"name": "Читатель", "email": "reader@example.com"},
    ).json()
    return {
        "book_id": book["id"],
        "reader_id": reader["id"],
        "loan_date": "2026-09-30",
        "returned": changed,
    }


@pytest.mark.parametrize("resource", RESOURCES)
def test_crud(client, resource):
    created = client.post(f"/api/{resource}", json=payload(client, resource))
    assert created.status_code == 200
    item = created.json()

    listing = client.get(f"/api/{resource}")
    assert listing.status_code == 200
    assert item in listing.json()

    updated = client.put(
        f"/api/{resource}/{item['id']}",
        json=payload(client, resource, changed=True),
    )
    assert updated.status_code == 200

    deleted = client.delete(f"/api/{resource}/{item['id']}")
    assert deleted.status_code == 204
    assert all(row["id"] != item["id"] for row in client.get(f"/api/{resource}").json())
