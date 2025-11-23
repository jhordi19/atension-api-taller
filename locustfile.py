from locust import HttpUser, task, between

class ATensionUser(HttpUser):
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        # Autenticación: reemplaza con un usuario y contraseña válidos
        response = self.client.post(
            "/api/v1/auth/token",
            data={
                "username": "consuelo@gmail.com",
                "password": "Consuelo123"
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token")
        else:
            self.token = None

    @task
    def get_pressures(self):
        if self.token:
            self.client.get(
                "/api/v1/pressures?page=1&limit=5",
                headers={"Authorization": f"Bearer {self.token}"}
            )

    @task
    def create_pressure(self):
        if self.token:
            self.client.post(
                "/api/v1/pressures",
                json={
                    "systolic": 120,
                    "diastolic": 80,
                    "taken_at": "2025-11-22T12:00:00"
                },
                headers={"Authorization": f"Bearer {self.token}"}
            )

    @task
    def get_profile(self):
        if self.token:
            self.client.get(
                "/api/v1/auth/me",
                headers={"Authorization": f"Bearer {self.token}"}
            )

