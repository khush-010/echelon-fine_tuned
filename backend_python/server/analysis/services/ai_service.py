def generate_response(user_data):
    if not user_data:
        return "Could not analyze this account."

    return f"""
    Account Analysis:

    Name: {user_data['name']}
    Bio: {user_data['bio']}
    Followers: {user_data['followers']}
    Total Tweets: {user_data['tweets']}

    This profile shows strong engagement potential.
    """
