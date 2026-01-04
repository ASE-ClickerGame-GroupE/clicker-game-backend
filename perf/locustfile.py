import os
import time
import random
from locust import HttpUser, task, between

USER_SVC = os.getenv("USER_SVC", "http://127.0.0.1:8000")
GAME_SVC = os.getenv("GAME_SVC", "http://127.0.0.1:8001")
#LEADER_SVC = os.getenv("LEADER_SVC", "http://127.0.0.1:8002")

TEST_LOGIN = os.getenv("TEST_LOGIN", "testuser")
TEST_PASSWORD = os.getenv("TEST_PASSWORD", "secret123")
CREATE_USER_ON_START = os.getenv("CREATE_USER_ON_START", "false").lower() == "true"
ENABLE_LEADERBOARD = os.getenv("ENABLE_LEADERBOARD", "false").lower() == "true"


class ClickerMicroservicesUser(HttpUser):
    host = "http://127.0.0.1"
    wait_time = between(0.2, 1.0)

    def on_start(self):
        self.auth_headers = {}
        self.session_id = None

        self.client.get(f"{USER_SVC}/health", name="user/health")
        self.client.get(f"{GAME_SVC}/health", name="game/health")

        if CREATE_USER_ON_START:
            unique = f"{TEST_LOGIN}_{int(time.time())}_{random.randint(1000,9999)}"
            signup_payload = {
                "login": unique,
                "password": TEST_PASSWORD,
                "email": f"{unique}@example.com",
            }

            with self.client.post(
                f"{USER_SVC}/auth/signup",
                json=signup_payload,
                name="user/auth/signup",
                catch_response=True,
            ) as r:
                if r.status_code not in (200, 201):
                    r.failure(f"Signup failed: {r.status_code} {r.text}")
                    return

            login_value = unique
        else:
            login_value = TEST_LOGIN

        with self.client.post(
            f"{USER_SVC}/auth/token",
            data={"username": login_value, "password": TEST_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            name="user/auth/token",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Login failed: {resp.status_code} {resp.text}")
                return

            token = resp.json().get("access_token")
            if not token:
                resp.failure("No access_token in login response")
                return

        self.auth_headers = {"Authorization": f"Bearer {token}"}

    @task(5)
    def start_and_finish(self):
        if not self.auth_headers:
            return

        with self.client.post(
            f"{GAME_SVC}/game/start",
            headers=self.auth_headers,
            name="game/game/start",
            catch_response=True,
        ) as resp:
            if resp.status_code not in (200, 201):
                resp.failure(f"Start game failed: {resp.status_code} {resp.text}")
                return

            session_id = resp.json().get("session_id")
            if not session_id:
                resp.failure("No session_id returned")
                return

        with self.client.post(
            f"{GAME_SVC}/game/finish",
            headers=self.auth_headers,
            json={
                "session_id": session_id,
                "scores": {},
                "finished_at": time.time(),
            },
            name="game/game/finish",
            catch_response=True,
        ) as resp:
            if resp.status_code != 200:
                resp.failure(f"Finish failed: {resp.status_code} {resp.text}")

    @task(2)
    def list_games(self):
        if not self.auth_headers:
            return

        self.client.get(
            f"{GAME_SVC}/game",
            headers=self.auth_headers,
            name="game/game/list",
        )

    #@task(1)
    #def leaderboard_health(self):
     #   if not ENABLE_LEADERBOARD:
      #      return

       # self.client.get(f"{LEADER_SVC}/health", name="leader/health")
