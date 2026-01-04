import os
import time
import random
from locust import HttpUser, task, between

# Services
USER_SVC = os.getenv("USER_SVC", "http://127.0.0.1:8000")
GAME_SVC = os.getenv("GAME_SVC", "http://127.0.0.1:8001")
LEADER_SVC = os.getenv("LEADER_SVC", "http://127.0.0.1:8002")  # placeholder

# Credentials (user-service uses OAuth2PasswordRequestForm)
TEST_LOGIN = os.getenv("TEST_LOGIN", "testuser")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "secret123")

# Optional: auto signup (heavy under load)
CREATE_USER_ON_START = os.getenv("CREATE_USER_ON_START", "false").lower() == "true"


class ClickerMicroservicesUser(HttpUser):
    wait_time = between(0.2, 1.0)

    def on_start(self):
        # Health checks (absolute URLs)
        self.client.get(f"{USER_SVC}/health", name="user/health")
        self.client.get(f"{GAME_SVC}/health", name="game/health")

        # Optional signup (JSON)
        if CREATE_USER_ON_START:
            unique = f"{TEST_LOGIN}_{int(time.time())}_{random.randint(1000,9999)}"
            signup_payload = {
                "loging": unique,
                "password": TEST_PASSWORD,
                "email": f"{unique}@example.com",
            }
            self.client.post(f"{USER_SVC}/auth/signup", json=signup_payload, name="user/auth/signup")
            login_value = unique
        else:
            login_value = TEST_LOGIN

        # Login (FORM URLENCODED)
        with self.client.post(
            f"{USER_SVC}/auth/token",
            data={"username": login_value, "password": TEST_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            name="user/auth/token",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Login failed: {resp.status_code} {resp.text}")
                self.auth_headers = {}
                return

            token = resp.json().get("access_token")
            if not token:
                resp.failure("No access_token in login response")
                self.auth_headers = {}
                return

        self.auth_headers = {"Authorization": f"Bearer {token}"}
        self.session_id = None
        self.current_score = 0

    @task(5)
    def play_game_flow(self):
        # Start game (auth required)
        with self.client.post(
            f"{GAME_SVC}/game/start",
            headers=self.auth_headers,
            name="game/game/start",
            catch_response=True,
        ) as resp:
            if resp.status_code not in (200, 201):
                resp.failure(f"Start game failed: {resp.status_code} {resp.text}")
                return

            self.session_id = resp.json().get("session_id")
            if not self.session_id:
                resp.failure("No session_id returned")
                return

        # Click events (your /game/click currently has no auth)
        clicks = random.randint(8, 20)
        score_estimate = 0

        for _ in range(clicks):
            hit = random.random() < 0.75
            reaction_ms = random.randint(120, 600)

            with self.client.post(
                f"{GAME_SVC}/game/click",
                json={"session_id": self.session_id, "hit": hit, "reaction_ms": reaction_ms},
                name="game/game/click",
                catch_response=True,
            ) as resp:
                if resp.status_code != 200:
                    resp.failure(f"Click failed: {resp.status_code} {resp.text}")
                    return
                score_estimate = resp.json().get("scores", score_estimate)

        self.current_score = score_estimate

        # Finish game (auth required)
        finished_at = time.time()
        with self.client.post(
            f"{GAME_SVC}/game/finish",
            headers=self.auth_headers,
            json={"session_id": self.session_id, "scores": self.current_score, "finished_at": finished_at},
            name="game/game/finish",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Finish failed: {resp.status_code} {resp.text}")
                return

        # Leaderboard placeholder (replace when you paste endpoints)
        # self.client.post(f"{LEADER_SVC}/scores", headers=self.auth_headers,
        #                  json={"session_id": self.session_id, "score": self.current_score},
        #                  name="leader/scores/submit")

    @task(2)
    def list_games(self):
        self.client.get(
            f"{GAME_SVC}/game",
            headers=self.auth_headers,
            name="game/game/list",
        )

    @task(1)
    def leaderboard_health(self):
        self.client.get(f"{LEADER_SVC}/health", name="leader/health")
