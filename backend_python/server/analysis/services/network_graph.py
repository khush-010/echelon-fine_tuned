import networkx as nx
from networkx.readwrite import json_graph

import networkx as nx
from networkx.readwrite import json_graph

def build_follower_graph(api_response: dict, target_username: str, limit=20):
    """
    Build ego network graph from Twitter followers API response
    """

    G = nx.Graph()

    G.add_node(
        target_username,
        label=target_username,
        color="red",
        size=35,
        role="target"
    )

    instructions = api_response["result"]["timeline"]["instructions"]

    followers_added = 0

    for ins in instructions:
        if "entries" not in ins:
            continue

        for entry in ins["entries"]:
            if followers_added >= limit:
                break

            try:
                legacy = entry["content"]["itemContent"]["user_results"]["result"]["legacy"]

                username = legacy["screen_name"]

                G.add_node(
                    username,
                    label=username,
                    followers=legacy["followers_count"],
                    following=legacy["friends_count"],
                    tweets=legacy["statuses_count"],
                    verified=legacy["verified"],
                    bio=legacy["description"],
                    profile_image=legacy["profile_image_url_https"],
                    color="blue",
                    size=15
                )

                # follower → target
                G.add_edge(username, target_username)

                followers_added += 1

            except KeyError:
                continue

    return json_graph.node_link_data(G)
