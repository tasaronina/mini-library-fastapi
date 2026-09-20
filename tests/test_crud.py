"""Twenty CRUD checks: four actions for each of five resource types."""

import pytest
from fastapi.testclient import TestClient

from library.main import app


RESOURCES = ("authors", "genres", "books", "readers", "loans")


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("LIBRARY_DB_PATH", str(tmp_path / "test.db"))
    with TestClient(app) as test_client:
        yield test_client


def payload(client: TestClient, resource: str, changed: bool = False) -> dict:
    suffix = " обновлён" if changed else ""
    if resource == "authors":
        return {"name": "Автор" + suffix}
    if resource == "genres":
        return {"name": "Жанр" + suffix}
    if resource == "readers":
        return {"name": "Читатель" + suffix, "email": "reader@example.test"}
    if resource == "books":
        author = client.post("/api/authors", json={"name": "Автор"}).json()
        genre = client.post("/api/genres", json={"name": "Жанр"}).json()
        return {"title": "Книга" + suffix, "author_id": author["id"], "genre_id": genre["id"]}
    book = client.post("/api/books", json=payload(client, "books")).json()
    reader = client.post("/api/readers", json={"name": "Читатель", "email": "reader@example.test"}).json()
    return {
        "book_id": book["id"],
        "reader_id": reader["id"],
        "loan_date": "2026-09-20",
        "returned": changed,
    }


@pytest.mark.parametrize("resource", RESOURCES)
def test_create(client, resource):
    response = client.post(f"/api/{resource}", json=payload(client, resource))
    assert response.status_code == 201
    assert response.json()["id"] > 0


@pytest.mark.parametrize("resource", RESOURCES)
def test_read_list_and_one(client, resource):
    item = client.post(f"/api/{resource}", json=payload(client, resource)).json()
    listing = client.get(f"/api/{resource}")
    single = client.get(f"/api/{resource}/{item['id']}")
    assert listing.status_code == 200
    assert item in listing.json()
    assert single.status_code == 200
    assert single.json() == item


@pytest.mark.parametrize("resource", RESOURCES)
def test_update(client, resource):
    original = payload(client, resource)
    item = client.post(f"/api/{resource}", json=original).json()
    changed = dict(original)
    if resource == "books":
        changed["title"] = "Книга обновлена"
    elif resource == "loans":
        changed["returned"] = True
    else:
        changed["name"] = "Новое имя"
    response = client.put(f"/api/{resource}/{item['id']}", json=changed)
    assert response.status_code == 200
    for key, value in changed.items():
        assert response.json()[key] == value
    assert client.get(f"/api/{resource}/{item['id']}").json() == response.json()


@pytest.mark.parametrize("resource", RESOURCES)
def test_delete(client, resource):
    item = client.post(f"/api/{resource}", json=payload(client, resource)).json()
    response = client.delete(f"/api/{resource}/{item['id']}")
    assert response.status_code == 204
    assert client.get(f"/api/{resource}/{item['id']}").status_code == 404


def test_invalid_foreign_key_is_rejected(client):
    response = client.post(
        "/api/books",
        json={"title": "Несуществующий автор", "author_id": 999, "genre_id": 999},
    )
    assert response.status_code == 409


def test_parent_with_child_cannot_be_deleted(client):
    author = client.post("/api/authors", json={"name": "Автор"}).json()
    genre = client.post("/api/genres", json={"name": "Жанр"}).json()
    client.post(
        "/api/books",
        json={"title": "Книга", "author_id": author["id"], "genre_id": genre["id"]},
    )
    assert client.delete(f"/api/authors/{author['id']}").status_code == 409


def test_homepage_and_openapi(client):
    assert client.get("/").status_code == 200
    paths = client.get("/openapi.json").json()["paths"]
    methods = sum(len(operations) for path, operations in paths.items() if path.startswith("/api/"))
    assert methods == 25
