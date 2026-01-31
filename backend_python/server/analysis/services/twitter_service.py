import requests
from django.conf import settings


def fetch_twitter_user(username):
    url = "https://twitter241.p.rapidapi.com/user"

    querystring = {"username": username}
    print(settings.RAPIDAPI_KEY, settings.RAPIDAPI_HOST)
    headers = {
        "x-rapidapi-key": settings.RAPIDAPI_KEY,# remove the env variable and directly use the key herex
        "x-rapidapi-host": settings.RAPIDAPI_HOST
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=querystring,
            timeout=10
        )

        if response.status_code != 200:
            return None

        return response.json()

    except requests.RequestException:
        return None

def fetch_user_tweets(user_id,count=50):
        

    url = "https://twitter241.p.rapidapi.com/user-tweets"

    querystring = {"user":user_id,"count":count}
    headers = {
        "x-rapidapi-key": settings.RAPIDAPI_KEY,
        "x-rapidapi-host": settings.RAPIDAPI_HOST
    }

    response = requests.get(url, headers=headers, params=querystring)

    try:
        if response.status_code != 200:
            return None

        return response.json()
    except requests.RequestException:
        return None

def clean_user_features(api_response, target=None):
    """
    Extract and transform required features
    to exactly match ML model expectations.
    """

    try:
        user = (
            api_response["result"]
            ["data"]
            ["user"]
            ["result"]
        )

        legacy = user.get("legacy", {})

        # -------------------------------
        # Helper Converters
        # -------------------------------
        def bool_to_int(value):
            return 1 if value else 0

        def safe_int(value):
            try:
                return int(value)
            except (TypeError, ValueError):
                return 0

        # -------------------------------
        # Language Encoding
        # IMPORTANT: Must match training
        # -------------------------------
        lang_map = {
            "en": 1,
            "es": 2,
            "fr": 3,
            "de": 4,
        }

        lang_num = lang_map.get(legacy.get("lang"), 0)

        # -------------------------------
        # Final Ordered Features
        # -------------------------------
        cleaned_data = {
            "id": safe_int(user.get("rest_id")),
            "favourites_count": safe_int(legacy.get("favourites_count")),
            "followers_count": safe_int(legacy.get("followers_count")),
            "statuses_count": safe_int(legacy.get("statuses_count")),
            "friends_count": safe_int(legacy.get("friends_count")),
            "default_profile": bool_to_int(legacy.get("default_profile")),
            "default_profile_image": bool_to_int(legacy.get("default_profile_image")),
            "profile_use_background_image": bool_to_int(
                legacy.get("profile_use_background_image")
            ),
            "utc_offset": safe_int(legacy.get("utc_offset")),
            "listed_count": safe_int(legacy.get("listed_count")),
            "geo_enabled": bool_to_int(legacy.get("geo_enabled")),
            "lang_num": lang_num,
        }
        
        cleaned_array = [[
            cleaned_data["id"],
            cleaned_data["favourites_count"],
            cleaned_data["followers_count"],
            cleaned_data["statuses_count"],
            cleaned_data["friends_count"],
            cleaned_data["default_profile"],
            cleaned_data["default_profile_image"],
            cleaned_data["profile_use_background_image"],
            cleaned_data["utc_offset"],
            cleaned_data["listed_count"],
            cleaned_data["geo_enabled"],
            cleaned_data["lang_num"],
        ]]
        
        


        return cleaned_array

    except KeyError:
        return None
