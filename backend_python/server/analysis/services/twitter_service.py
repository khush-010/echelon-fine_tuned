import requests
from django.conf import settings


def fetch_twitter_user(username):
    url = "https://twitter241.p.rapidapi.com/user"

    querystring = {"username": username}
    print(settings.RAPIDAPI_KEY, settings.RAPIDAPI_HOST)
    headers = {
        "x-rapidapi-key": settings.RAPIDAPI_KEY,# remove the env variable and directly use the key here
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

def clean_user_features(api_response, target=None):
    """
    Extract only required features from RapidAPI Twitter response.
    """

    try:
        user = (
            api_response["result"]
            ["data"]
            ["user"]
            ["result"]
        )

        legacy = user.get("legacy", {})
        verification = user.get("verification", {})
        privacy = user.get("privacy", {})

        cleaned_data = {
            "tweet": legacy.get("statuses_count"),
            "followers_count": legacy.get("followers_count"),
            "friends_count": legacy.get("friends_count"),
            "favourites_count": legacy.get("favourites_count"),
            "listed_count": legacy.get("listed_count"),
            "url": legacy.get("url"),
            "lang": legacy.get("lang"),
            "default_profile": legacy.get("default_profile"),
            "default_profile_image": legacy.get("default_profile_image"),
            "geo_enabled": legacy.get("geo_enabled"),
            "follow_request_sent": legacy.get("follow_request_sent"),
            "statuses_count": legacy.get("statuses_count"),
            "verified": verification.get("verified"),
            "protected": privacy.get("protected"),
        }

        return cleaned_data

    except KeyError:
        return None
