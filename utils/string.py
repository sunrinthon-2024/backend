from urllib.parse import urlencode


def create_url(url: str, **kwargs) -> str:
    return url + urlencode(kwargs)


def get_country_locality_string(address_components: dict):
    content = address_components["plus_code"]["compound_code"]
    parts = content.split(",")
    return ",".join(parts[1:]).strip()
