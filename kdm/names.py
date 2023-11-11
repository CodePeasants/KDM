import os
import json
from names_dataset import NameDataset


NAME_COUNTRIES = ["US", "JP", "CA", "GB", "IT"]

_DIR = os.path.dirname(__file__)
CACHE_PATH = os.path.join(_DIR, "resources", "names.json")
NAME_CACHE = None


def get_name(gender, exclude=None):
    cache = get_name_cache()
    names = cache[gender]
    if exclude:
        names = list(set(names) - set(exclude))
    return names[0]


def get_name_cache(refresh=False):
    global NAME_CACHE

    if NAME_CACHE is None:
        if not refresh and os.path.exists(CACHE_PATH):
            with open(CACHE_PATH, "r", encoding="utf-8") as fh:
                NAME_CACHE = json.load(fh)
        else:
            cache_names()
    return NAME_CACHE


def cache_names(count=200, countries=None):
    global NAME_CACHE
    if os.path.exists(CACHE_PATH):
        os.remove(CACHE_PATH)
    
    data = NameDataset()
    if countries is None:
        countries = NAME_COUNTRIES
    
    result = {"M": [], "F": []}
    for country in countries:
        top_names = data.get_top_names(n=count, country_alpha2=country)
        result["M"].extend(top_names[country]["M"])
        result["F"].extend(top_names[country]["F"])
    
    with open(CACHE_PATH, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=4)
    
    NAME_CACHE = result
