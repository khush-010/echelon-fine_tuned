from http import HTTPStatus
import networkx as nx
from rest_framework.response import Response

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

    for entry in instructions[3]["entries"]:
        if entry is None:
            continue

        
        if followers_added >= limit:
            break

        try:
            result = entry["content"]["itemContent"]["user_results"]["result"]
            username = result["core"]["name"]
            
            G.add_node(
                username,
                label=username,
                followers=result["legacy"]["followers_count"],
                following=result["legacy"]["friends_count"],
                tweets=result["legacy"]["statuses_count"],
                bio=result["legacy"]["description"],
                # profile_image=result["legacy"]["profile_image_url_https"],
                color="blue",
                size=15
            )

            # follower → target
            G.add_edge(username, target_username)

            followers_added += 1

        except KeyError:
            print(KeyError)
            continue
    data = json_graph.node_link_data(G)
    return Response(data, HTTPStatus.OK)

