import requests
from requests import Response


class HttpClient:

    def __init__(self):
        # fallback if response encoding unspecified
        self.defaultEncoding = 'utf-8'

    # returns raw response text or throws if 4/5xx response
    def getRequest(self, fullPath: str, **kwargs) -> 'Response':
        res = requests.get(fullPath, **kwargs)
        if res.status_code >= 400:
            raise RuntimeError(f"received a {res.status_code} status code for: {fullPath}.")
        if not res.encoding:
            res.encoding = self.defaultEncoding
        return res

httpClient = HttpClient()