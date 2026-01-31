from datetime import datetime, timezone
from collections import defaultdict
from fractions import Fraction
from decimal import Decimal
import math


def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def safe_float(value):
    try:
        v = float(value)
        return v if math.isfinite(v) else 0.0
    except (TypeError, ValueError):
        return 0.0


def safe_mean(values):
    clean = []
    for v in values:
        if isinstance(v, (int, float)):
            v = float(v)
            if math.isfinite(v):
                clean.append(v)
        elif isinstance(v, (Fraction, Decimal)):
            v = float(v)
            if math.isfinite(v):
                clean.append(v)
        elif isinstance(v, str) and v.isdigit():
            clean.append(float(v))

    if not clean:
        return 0.0

    return sum(clean) / len(clean)


def build_interaction_network(tweets):
    interaction_counts = {
        "reply": 0,
        "mention": 0,
        "retweet": 0,
        "quote": 0
    }

    for t in tweets:
        text = t.get("text", "")

        if t.get("is_retweet"):
            interaction_counts["retweet"] += 1

        if text.startswith("@"):
            interaction_counts["reply"] += 1

        if "@" in text and not text.startswith("@"):
            interaction_counts["mention"] += text.count("@")

        if t.get("is_quote"):
            interaction_counts["quote"] += 1

    nodes = [
        {"id": "self", "label": "Account", "type": "center"}
    ]

    edges = []

    for key, count in interaction_counts.items():
        if count > 0:
            nodes.append({
                "id": key,
                "label": key.capitalize(),
                "count": count
            })
            edges.append({
                "from": "self",
                "to": key,
                "weight": count
            })

    return {
        "nodes": nodes,
        "edges": edges
    }


def aggregate_twitter_data(api_response, account_age_days=None):
    """
    Content-only Twitter/X analytics.
    Engagement = Engagement Rate by Impressions (ERi).
    Retweets excluded.
    Time-based dynamic activity timeline.
    """

    try:
        instructions = api_response["result"]["timeline"]["instructions"]
    except (KeyError, TypeError):
        return None

    tweets = []
    user_legacy = None

    for instruction in instructions:
        if instruction.get("type") != "TimelineAddEntries":
            continue

        for entry in instruction.get("entries", []):
            content = entry.get("content", {})

            if content.get("entryType") == "TimelineTimelineItem":
                tweet = extract_tweet(content.get("itemContent", {}))
                if tweet:
                    tweets.append(tweet)
                    if not user_legacy:
                        user_legacy = tweet["user"]

            elif content.get("entryType") == "TimelineTimelineModule":
                for item in content.get("items", []):
                    tweet = extract_tweet(
                        item.get("item", {}).get("itemContent", {})
                    )
                    if tweet:
                        tweets.append(tweet)
                        if not user_legacy:
                            user_legacy = tweet["user"]

    if not user_legacy:
        return None

    followers = safe_int(user_legacy.get("followers_count"))
    following = safe_int(user_legacy.get("friends_count"))
    total_posts = safe_int(user_legacy.get("statuses_count"))
    verified = bool(user_legacy.get("verified", False))

    account_age_days = account_age_days or 0

    posts_per_day = (
        total_posts / account_age_days
        if account_age_days > 0 else 0.0
    )

    originals = [
        t for t in tweets
        if not t["is_retweet"] and t["views"] > 0
    ]

    total_likes = sum(t["likes"] for t in originals)
    total_replies = sum(t["replies"] for t in originals)
    total_retweets = sum(t["retweets"] for t in originals)
    total_views = sum(t["views"] for t in originals)

    total_engagement = total_likes + total_replies + total_retweets

    view_engagement_rate = (
        math.log1p(total_engagement) / math.log1p(total_views)
        if total_views > 0 else 0.0
    )

    view_engagement_rate = safe_float(view_engagement_rate)

    avg_likes = safe_mean([t["likes"] for t in originals])
    avg_comments = safe_mean([t["replies"] for t in originals])
    avg_retweets = safe_mean([t["retweets"] for t in originals])
    avg_views = safe_mean([t["views"] for t in originals])

    timestamps = [
        t["created_at"]
        for t in tweets
        if isinstance(t["created_at"], datetime)
    ]

    timeline_data = defaultdict(lambda: {"posts": 0, "engagement": 0})

    if timestamps:
        start = min(timestamps)
        end = max(timestamps)
        span_days = (end - start).days

        if span_days <= 7:
            fmt = "%Y-%m-%d %H:00"
        elif span_days <= 30:
            fmt = "%Y-%m-%d"
        elif span_days <= 180:
            fmt = "%Y-W%U"
        else:
            fmt = "%Y-%m"

        for t in tweets:
            if not isinstance(t["created_at"], datetime):
                continue

            key = t["created_at"].strftime(fmt)
            timeline_data[key]["posts"] += 1

            if not t["is_retweet"]:
                timeline_data[key]["engagement"] += (
                    t["likes"] + t["replies"] + t["retweets"]
                )

        activity_history = [
            {"time": k, **v}
            for k, v in sorted(timeline_data.items())
        ]
    else:
        activity_history = []

    behavior_scores = [
        {
            "category": "Posting Activity",
            "score": min(posts_per_day * 5, 100)
        },
        {
            "category": "Content Engagement",
            "score": min(view_engagement_rate * 120, 100)
        },
        {
            "category": "Account Longevity",
            "score": min(account_age_days / 50, 100)
        },
    ]

    fake_probability = min(
        (1 - view_engagement_rate) * 0.6
        + (posts_per_day / 80) * 0.4,
        1
    )

    if verified:
        fake_probability *= 0.3

    if fake_probability > 0.7:
        risk_level = "high"
    elif fake_probability > 0.4:
        risk_level = "medium"
    else:
        risk_level = "low"

    signals = []

    if view_engagement_rate < 0.003:
        signals.append("Low engagement relative to impressions")

    if posts_per_day > 50:
        signals.append("High posting frequency detected")

    if originals and (len(originals) / len(tweets)) < 0.3:
        signals.append("Heavy reliance on retweets")

    network_graph = build_interaction_network(tweets)

    return {
        "username": user_legacy.get("screen_name"),
        "fake_probability": round(fake_probability, 2),
        "risk_level": risk_level,
        "confidence": 0.95,
        "account_age_days": account_age_days,
        "verified": verified,
        "visual_metrics": {
            "engagement_rate_impressions": round(view_engagement_rate, 5),
            "posts_per_day": round(posts_per_day, 2),
            "followers": followers,
            "following": following,
            "avg_likes": round(avg_likes, 2),
            "avg_comments": round(avg_comments, 2),
            "avg_retweets": round(avg_retweets, 2),
            "avg_views": round(avg_views, 2),
            "original_post_ratio": round(
                len(originals) / len(tweets), 2
            ) if tweets else 0,
        },
        "activity_history": activity_history,
        "behavior_scores": behavior_scores,
        "network_graph": network_graph,
        "signals": signals,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


def extract_tweet(content):
    try:
        tweet_data = content["tweet_results"]["result"]
        legacy = tweet_data["legacy"]
        user = tweet_data["core"]["user_results"]["result"]["legacy"]

        created_at = datetime.strptime(
            legacy["created_at"],
            "%a %b %d %H:%M:%S %z %Y"
        )

        is_retweet = (
            "retweeted_status_result" in legacy
            or legacy.get("full_text", "").startswith("RT @")
        )

        return {
            "created_at": created_at,
            "is_retweet": is_retweet,
            "is_quote": "quoted_status_result" in legacy,
            "likes": safe_int(legacy.get("favorite_count")) if not is_retweet else 0,
            "replies": safe_int(legacy.get("reply_count")) if not is_retweet else 0,
            "retweets": safe_int(legacy.get("retweet_count")) if not is_retweet else 0,
            "views": (
                safe_int(tweet_data.get("views", {}).get("count"))
                if not is_retweet else 0
            ),
            "text": legacy.get("full_text", ""),
            "user": user,
        }

    except Exception:
        return None
