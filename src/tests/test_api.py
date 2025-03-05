import pytest
from httpx import AsyncClient
from src.db.api import app


@pytest.mark.asyncio
async def test_create_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/users/", json={"name": "John Doe", "email": "john@example.com"}
        )
    assert response.status_code == 200
    assert response.json()["name"] == "John Doe"
    assert response.json()["email"] == "john@example.com"


async def test_read_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Assuming a user with ID 1 exists
        response = await ac.get("/users/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1


async def test_delete_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Assuming a user with ID 1 exists and can be deleted
        response = await ac.delete("/users/1")
    assert response.status_code == 204


async def test_update_user():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(
            "/users/1", json={"name": "Jane Doe", "email": "jane@example.com"}
        )
    assert response.status_code == 200
    assert response.json()["name"] == "Jane Doe"


async def test_create_ipl_schedule():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/iplschedule/", json={"match": "Match 1", "date": "2024-04-05"}
        )
    assert response.status_code == 200
    assert response.json()["match"] == "Match 1"


async def test_read_ipl_schedule():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/iplschedule/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Expecting a list of schedules
