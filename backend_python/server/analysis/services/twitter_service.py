from datetime import datetime, timezone
import requests
from django.conf import settings



def fetch_twitter_user(username):
    url = "https://twitter241.p.rapidapi.com/user"

    querystring = {"username": username}
    headers = {
        "x-rapidapi-key": settings.RAPIDAPI_KEY,
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

def clean_user_features(api_response, tweets_per_days):
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

        def bool_to_int(value):
            return 1 if value else 0

        def safe_int(value):
            try:
                return int(value)
            except (TypeError, ValueError):
                return 0

        lang_map = {
            "en": 1,
            "es": 2,
            "fr": 3,
            "de": 4,
        }

        lang_num = lang_map.get(legacy.get("lang"), 0)
        created_at_str = api_response["result"]["data"]["user"]["result"]["core"]["created_at"]
        account_created = datetime.strptime(
            created_at_str,
            "%a %b %d %H:%M:%S %z %Y"
        )
        account_age_days = (datetime.now(timezone.utc) - account_created).days
        followers_count = safe_int(legacy.get("followers_count"))
        friends_count = safe_int(legacy.get("friends_count"))
        ff_ratio = (followers_count / (friends_count + 1)) 
        
        cleaned_data = {
            "favourites_count": safe_int(legacy.get("favourites_count")),
            "followers_count": followers_count,
            "statuses_count": safe_int(legacy.get("statuses_count")),
            "friends_count": friends_count,
            "default_profile": bool_to_int(legacy.get("default_profile")),
            "default_profile_image": bool_to_int(legacy.get("default_profile_image")),
            "profile_use_background_image": bool_to_int(
                legacy.get("profile_use_background_image")
            ),
            "utc_offset": safe_int(legacy.get("utc_offset")),
            "listed_count": safe_int(legacy.get("listed_count")),
            "geo_enabled": bool_to_int(legacy.get("geo_enabled")),
            "lang_num": lang_num,
            "account_age_days": safe_int(account_age_days),
            "tweets_per_days": safe_int(tweets_per_days),
            "ff_ratio": ff_ratio,
        }
        
        cleaned_array = [[
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
            cleaned_data["account_age_days"],
            cleaned_data["tweets_per_days"],
            cleaned_data["ff_ratio"],
        ]]
        
        


        return cleaned_array

    except KeyError:
        return None


def clean_tweets_api_response(data: dict) -> list[list]:
    """
    Extract cleaned tweet data as array format:
    [
        text:str,
        retweet_count:int,
        reply_count:int,
        favorite_count:int,
        num_hashtags:int,
        num_urls:int,
        num_mentions:int
    ]
    """

    cleaned_tweets = []

    instructions = data.get("result", {}).get("timeline", {}).get("instructions", [])

    for instruction in instructions:
        if instruction.get("type") != "TimelineAddEntries":
            continue

        entries = instruction.get("entries", [])

        for entry in entries:
            content = entry.get("content", {})
            entry_type = content.get("entryType")

            # Case 1: Single Tweet
            if entry_type == "TimelineTimelineItem":
                tweet = (
                    content.get("itemContent", {})
                    .get("tweet_results", {})
                    .get("result", {})
                )

                extracted = _extract_tweet_array(tweet)
                if extracted:
                    cleaned_tweets.append(extracted)

            # Case 2: Conversation Thread
            elif entry_type == "TimelineTimelineModule":
                items = content.get("items", [])

                for item in items:
                    tweet = (
                        item.get("item", {})
                        .get("itemContent", {})
                        .get("tweet_results", {})
                        .get("result", {})
                    )

                    extracted = _extract_tweet_array(tweet)
                    if extracted:
                        cleaned_tweets.append(extracted)

    return cleaned_tweets


def _extract_tweet_array(tweet: dict) -> list | None:
    """
    Extract required fields from tweet in array format.
    """

    if not tweet or "legacy" not in tweet:
        return None

    legacy = tweet["legacy"]
    entities = legacy.get("entities", {})

    text = legacy.get("full_text", "")
    retweet_count = legacy.get("retweet_count", 0)
    reply_count = legacy.get("reply_count", 0)
    favorite_count = legacy.get("favorite_count", 0)

    num_hashtags = len(entities.get("hashtags", []))
    num_urls = len(entities.get("urls", []))
    num_mentions = len(entities.get("user_mentions", []))

    return [
        text,
        retweet_count,
        reply_count,
        favorite_count,
        num_hashtags,
        num_urls,
        num_mentions,
    ]


def get_followers_username(user_id,count=10):
    url = "https://twitter241.p.rapidapi.com/followers"

    headers = {
        "x-rapidapi-key": settings.RAPIDAPI_KEY,
        "x-rapidapi-host": settings.RAPIDAPI_HOST
    }
    querystring = {"user":user_id,"count":count}
    response = requests.get(url, headers=headers,params=querystring)
    try:
        if response.status_code != 200:
            return None

        return response.json()
    except requests.RequestException:
        return None