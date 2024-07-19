from urllib.parse import urlencode


def create_url(url: str, **kwargs) -> str:
    return url + urlencode(kwargs)
