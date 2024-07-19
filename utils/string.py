from urllib.parse import urlencode


def create_url(url: str, **kwargs) -> str:
    return url + urlencode(kwargs)


def get_country_locality_string(address_components: dict):
    country = None
    locality = None

    for component in address_components:
        if "country" in component["types"]:
            country = component["long_name"]
        elif "locality" in component["types"]:
            locality = component["long_name"]

    if country and locality:
        return f"{locality}, {country}"
    else:
        return address_components["plus_code"]["compound_name"]
