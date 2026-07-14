import requests


class HTTPClient:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.session = requests.Session()

        self.session.headers.update(
            {
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/138.0.0.0 Safari/537.36"
                )
            }
        )

    def get(self, url: str) -> requests.Response:
        response = self.session.get(
            url,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response