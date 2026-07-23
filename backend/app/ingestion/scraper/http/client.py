import requests
from typing import Optional


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

    def get(
        self,
        url: str,
        *,
        params: Optional[dict] = None,
        headers: Optional[dict] = None,
    ) -> requests.Response:
        response = self.session.get(
            url,
            params=params,
            headers=headers,
            timeout=self.timeout,
        )

        response.raise_for_status()

        return response