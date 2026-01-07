import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch
from leaderboard_service.app.main import app
from leaderboard_service.app.auth_deps import TokenData, get_current_user  # <--- IMPORT THIS


@pytest.mark.asyncio
async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_get_total_score_leaderboard():
    fake_data = [{
        "id": "u1", "userName": "Player1", "totalGames": 5,
        "totalScores": 100, "bestScore": None, "place": 1
    }]

    with patch("leaderboard_service.app.main.get_leaderboard", new=AsyncMock(return_value=fake_data)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/leaderboard/total-score")

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["userName"] == "Player1"


@pytest.mark.asyncio
async def test_get_me_leaderboard_success():
    fake_entry = [{
        "id": "u1", "userName": "Me", "totalGames": 10,
        "totalScores": 500, "bestScore": None, "place": 5
    }]

    # Mock the Auth Dependency
    fake_user = TokenData(user_id="u1", loging="Me")
    with patch("leaderboard_service.app.main.get_leaderboard", new=AsyncMock(return_value=fake_entry)):
        app.dependency_overrides[get_current_user] = lambda: fake_user

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/leaderboard/total-score/me")

        app.dependency_overrides = {}

    assert response.status_code == 200
    assert response.json()["userName"] == "Me"


@pytest.mark.asyncio
async def test_get_me_leaderboard_not_found():
    with patch("leaderboard_service.app.main.get_leaderboard", new=AsyncMock(return_value=[])):
        fake_user = TokenData(user_id="u1", loging="Me")

        app.dependency_overrides[get_current_user] = lambda: fake_user

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/leaderboard/total-score/me")

        app.dependency_overrides = {}

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_best_single_run_leaderboard():
    fake_data = [
        {"id": "u1", "userName": "Player1", "totalGames": 5, "totalScores": None, "bestScore": 100, "place": 1}]

    with patch("leaderboard_service.app.main.get_leaderboard", new=AsyncMock(return_value=fake_data)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/leaderboard/best-single-run")

    assert response.status_code == 200
    assert response.json()[0]["bestScore"] == 100


@pytest.mark.asyncio
async def test_get_best_single_run_me():
    fake_data = [{"id": "u1", "userName": "Me", "totalGames": 5, "totalScores": None, "bestScore": 999, "place": 1}]
    fake_user = TokenData(user_id="u1", loging="Me")

    with patch("leaderboard_service.app.main.get_leaderboard", new=AsyncMock(return_value=fake_data)):
        app.dependency_overrides[get_current_user] = lambda: fake_user

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/leaderboard/best-single-run/me")

        app.dependency_overrides = {}

    assert response.status_code == 200
    assert response.json()["bestScore"] == 999


@pytest.mark.asyncio
async def test_get_best_single_run_me_404():
    fake_user = TokenData(user_id="u1", loging="Me")

    with patch("leaderboard_service.app.main.get_leaderboard", new=AsyncMock(return_value=[])):
        app.dependency_overrides[get_current_user] = lambda: fake_user

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/leaderboard/best-single-run/me")

        app.dependency_overrides = {}

    assert response.status_code == 404