from typing import Optional

import requests
from locust import HttpUser, between, task

API_BASE_URL = "http://localhost:8000"


def login(username: str, password: str) -> Optional[str]:
    """This function calls the login endpoint of the API to authenticate the user and get a token.

    Args:
        username (str): email of the user
        password (str): password of the user

    Returns:
        Optional[str]: token if login is successful, None otherwise
    """
    url = f"{API_BASE_URL}/login"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    data = {
        "grant_type": "",
        "username": username,
        "password": password,
        "scope": "",
        "client_id": "",
        "client_secret": "",
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        return None


class APIUser(HttpUser):
    host = "http://localhost:8000"
    wait_time = between(1, 5)

    @task(1)
    def predict(self):
        token = login("admin@example.com", "admin")
        files = [("file", ("dog.jpeg", open("dog.jpeg", "rb"), "image/jpeg"))]
        headers = {"Authorization": f"Bearer {token}"}
        payload = {}
        self.client.post(
            "http://localhost:8000/model/predict",
            headers=headers,
            data=payload,
            files=files,
        )

    @task(2)
    def index(self):
        token = login("admin@example.com", "admin")
        headers = {"Authorization": f"Bearer {token}"}
        self.client.get("/user/", headers=headers)
