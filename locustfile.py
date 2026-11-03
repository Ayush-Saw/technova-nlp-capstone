from locust import HttpUser, task, between
import os
class GatewayUser(HttpUser):
    wait_time=between(0.2,1)
    @task
    def triage(self):
        self.client.post("/v1/triage",json={"ticket":"Cannot login after password reset"},headers={"X-API-Key":os.getenv("API_KEY","change-me-before-use")})
