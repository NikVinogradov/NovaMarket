import logging

from locust import HttpUser, between, task

logger = logging.getLogger(__name__)


class RateLimiterUser(HttpUser):
    wait_time = between(0.01, 0.05)

    @task(3)
    def web_requests(self):
        self._hit_api("web")

    @task(2)
    def mobile_requests(self):
        self._hit_api("mobile")

    def _hit_api(self, client_type):
        headers = {"Client-Type": client_type}
        name = f"/api/ ({client_type})"
        with self.client.get("/api/", headers=headers, name=name, catch_response=True) as response:
            if response.status_code in (429, 503):
                logger.warning("rate_limited_%s", client_type)
                response.failure(f"rate_limited_{client_type}")
            elif response.status_code != 200:
                response.failure(f"unexpected_{response.status_code}")
