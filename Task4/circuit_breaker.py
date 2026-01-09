import logging

from locust import HttpUser, between, task

logger = logging.getLogger(__name__)


class CircuitBreakerUser(HttpUser):
    wait_time = between(0.05, 0.2)

    @task(4)
    def error_requests(self):
        self._request("/logistics/error", "error")

    @task(1)
    def fast_requests(self):
        self._request("/logistics/fast", "fast")

    def _request(self, path, name):
        with self.client.get(path, name=f"/logistics/{name}", catch_response=True) as response:
            if response.status_code == 503 and "fallback" in response.text:
                if name == "fast":
                    logger.warning("circuit_breaker_open")
                response.failure("fallback")
            elif response.status_code >= 500:
                response.failure(f"upstream_{response.status_code}")
            elif response.status_code != 200:
                response.failure(f"unexpected_{response.status_code}")
