from datetime import datetime


def aggregate_twitter_data(api_response):
    """
    Converts RapidAPI user profile JSON into structured
    dashboard-ready metrics (no timeline data required).
    """

    try:
        user_data = api_response["result"]["data"]["user"]["result"]
        legacy = user_data["legacy"]
        core = user_data["core"]
    except KeyError:
        return None

    # ----------------------------------------
    # Basic Profile Data
    # ----------------------------------------
    username = core.get("screen_name")
    account_created = datetime.strptime(
        core.get("created_at"),
        "%a %b %d %H:%M:%S %z %Y"
    )

    followers = legacy.get("followers_count", 0)
    following = legacy.get("friends_count", 0)
    total_posts = legacy.get("statuses_count", 0)
    favourites = legacy.get("favourites_count", 0)

    verified = (
        user_data.get("is_blue_verified", False)
        or user_data.get("verification", {}).get("verified", False)
    )

    account_age_days = (
        datetime.utcnow() - account_created.replace(tzinfo=None)
    ).days

    posts_per_day = total_posts / account_age_days if account_age_days > 0 else 0
    network_ratio = following / followers if followers else 0

    # ----------------------------------------
    # Engagement Proxy (since tweets not available)
    # ----------------------------------------
    engagement_ratio = (
        favourites / total_posts if total_posts > 0 else 0
    )

    # ----------------------------------------
    # Behavior Scores (0-100 Normalization)
    # ----------------------------------------
    behavior_scores = [
        {"category": "Posting Pattern", "score": min(posts_per_day * 5, 100)},
        {"category": "Engagement Proxy", "score": min(engagement_ratio * 10, 100)},
        {"category": "Network", "score": min(network_ratio * 100, 100)},
        {"category": "Account Age", "score": min(account_age_days / 50, 100)},
        {"category": "Profile Completeness", "score": 100 if not legacy.get("default_profile_image") else 40},
    ]

    # ----------------------------------------
    # Fake Probability Logic
    # ----------------------------------------
    fake_probability = min(
        (network_ratio * 0.5)
        + (1 - engagement_ratio) * 0.3
        + (1 if legacy.get("default_profile_image") else 0) * 0.2,
        1
    )

    if verified:
        fake_probability *= 0.2  # reduce risk if verified

    if fake_probability > 0.7:
        risk_level = "high"
    elif fake_probability > 0.4:
        risk_level = "medium"
    else:
        risk_level = "low"

    # ----------------------------------------
    # Signals
    # ----------------------------------------
    signals = []

    if network_ratio > 2:
        signals.append("Mass-following behavior detected")

    if posts_per_day > 50:
        signals.append("High posting frequency detected")

    if legacy.get("default_profile_image"):
        signals.append("Default profile image detected")

    if followers < 50 and account_age_days > 365:
        signals.append("Low followers despite old account")

    # ----------------------------------------
    # Final Response
    # ----------------------------------------
    return {
        "username": username,
        "fake_probability": round(fake_probability, 2),
        "risk_level": risk_level,
        "confidence": 0.90,
        "account_age_days": account_age_days,
        "verified": verified,
        "visual_metrics": {
            "engagement_ratio_proxy": round(engagement_ratio, 4),
            "posts_per_day": round(posts_per_day, 2),
            "followers": followers,
            "following": following,
            "total_posts": total_posts,
            "favourites": favourites,
        },
        "behavior_scores": behavior_scores,
        "signals": signals,
        "timestamp": datetime.utcnow().isoformat(),
    }
