from uuid import uuid4
from locust import HttpUser, between, task

class TaskApiUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.headers = {}
        username = f"locust_{uuid4().hex}"
        password = "load-test-password"

        with self.client.post("/auth/register",
            json={"username": username, "password": password},
            name="/auth/register",
            catch_response=True,
        ) as response:
            if response.status_code >= 400:
                response.failure("Could not register load-test user")
                return
            response.success()

        with self.client.post("/auth/login",
            data={"username": username, "password": password},
            name="/auth/login",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure("Could not log in load-test user")
                return

            access_token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {access_token}"}
            response.success()

    @task(5)
    def create_task(self):
        self.client.post("/tasks/",
            json={"title": "Load test task",
                "description": "Created by Locust",
                "priority": 1,
            },
            headers=self.headers,
            name="/tasks/ [POST]",
        )

    @task(3)
    def read_tasks(self):
        self.client.get("/tasks/",
            headers=self.headers,
            name="/tasks/ [GET]",
        )

    @task(1)
    def search_tasks(self):
        self.client.get("/tasks/search",
            params={"q": "Load"},
            headers=self.headers,
            name="/tasks/search",
        )

    @task(1)
    def top_priority_tasks(self):
        self.client.get("/tasks/top",
            params={"n": 5},
            headers=self.headers,
            name="/tasks/top",
        )
