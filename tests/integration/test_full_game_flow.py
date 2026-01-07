import pytest
import pytest_asyncio
import os
from httpx import AsyncClient, ASGITransport
from motor.motor_asyncio import AsyncIOMotorClient

# Import the actual FastAPI apps
from user_service.app.main import app as user_app
from game_service.app.main import app as game_app

# Import the DB modules directly so we can patch them
from user_service.app import db as user_db
from game_service.app import db as game_db

# Shared Test Config
TEST_DB_NAME = "test_integration_db"
MONGO_URI = "mongodb://localhost:27017"

# We must ensure both apps use the same Secret for JWT to work
os.environ["SECRET_KEY"] = "integration_test_secret"
os.environ["ALGORITHM"] = "HS256"
os.environ["MONGODB_DB"] = TEST_DB_NAME


@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="module", loop_scope="module")
async def db_cleanup():
    # 1. Force User Service to use Test DB
    user_db.MONGODB_URI = MONGO_URI
    user_db.MONGODB_DB = TEST_DB_NAME
    user_db._client = None  # Reset client so it reconnects with new URI

    # 2. Force Game Service to use Test DB
    game_db.MONGODB_URI = MONGO_URI
    game_db.MONGODB_DB = TEST_DB_NAME
    game_db._client = None

    # 3. Clean the DB
    client = AsyncIOMotorClient(MONGO_URI)
    await client.drop_database(TEST_DB_NAME)
    yield
    # Clean after
    await client.drop_database(TEST_DB_NAME)


@pytest.mark.asyncio(loop_scope="module")
async def test_full_user_flow(db_cleanup):
    """
    Integration Test: Signup -> Login -> Start Game -> Finish Game -> Verify
    """

    # 1. SETUP CLIENTS
    # We use ASGITransport so we don't need to actually run the servers on ports.
    # We call the code directly in memory.
    async with AsyncClient(transport=ASGITransport(app=user_app), base_url="http://user-service") as user_client, \
            AsyncClient(transport=ASGITransport(app=game_app), base_url="http://game-service") as game_client:
        # ==========================================
        # STEP 1: SIGN UP (User Service)
        # ==========================================
        user_data = {
            "loging": "integration_player",
            "password": "securePassword123",
            "email": "player@test.com"
        }
        resp = await user_client.post("/auth/signup", json=user_data)
        assert resp.status_code == 200
        user_id = resp.json()["user_id"]
        print(f"DEBUG: User Created with ID: {user_id}")

        # ==========================================
        # STEP 2: LOG IN (User Service)
        # ==========================================
        login_data = {
            "username": "integration_player",  # OAuth2 form uses 'username' field
            "password": "securePassword123"
        }
        resp = await user_client.post("/auth/token", data=login_data)
        assert resp.status_code == 200
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print(f"DEBUG: Got Token: {token[:10]}...")

        # ==========================================
        # STEP 3: START GAME (Game Service)
        # ==========================================
        # The Game Service will decode the token using the shared SECRET_KEY
        resp = await game_client.post("/game/start", headers=headers)
        assert resp.status_code == 200
        session_id = resp.json()["session_id"]
        print(f"DEBUG: Game Started, Session ID: {session_id}")

        # ==========================================
        # STEP 4: FINISH GAME (Game Service)
        # ==========================================
        score_payload = {
            "session_id": session_id,
            "scores": {user_id: 150},
            "finished_at": 1700000000
        }
        resp = await game_client.post("/game/finish", headers=headers, json=score_payload)
        assert resp.status_code == 200
        assert resp.json()["session_id"] == session_id

        # ==========================================
        # STEP 5: VERIFY HISTORY (Game Service)
        # ==========================================
        resp = await game_client.get("/game", headers=headers)
        assert resp.status_code == 200
        history = resp.json()

        assert len(history) > 0
        latest_game = history[0]
        assert latest_game["id"] == session_id
        # Check specific score inside the dictionary
        assert latest_game["scores"][user_id] == 150
        assert latest_game["user_id"] == [user_id]