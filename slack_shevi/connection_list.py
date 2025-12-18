import os

from dotenv import load_dotenv
from slack_sdk import WebClient


load_dotenv()

def get_slack_client():
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    if not slack_token:
        raise ValueError("SLACK_BOT_TOKEN environment variable not set.")
    return WebClient(token=slack_token)


def create_connection_list(client):
    all_users = get_slack_users(client)

    return {
        channel.get("name", "N/A"): build_member_details(
            get_channel_members(client, channel["id"]),
            all_users
        )
        for channel in list_all_channels(client)
    }


def get_slack_users(client):
    users = paginate(client.users_list, "members", limit=200)
    return {user["id"]: user for user in users}


def list_all_channels(client, channel_types=("public_channel", "private_channel")):
    channels = []

    for channel_type in channel_types:
        channels.extend(
            paginate(
                client.conversations_list,
                "channels",
                types=channel_type,
                limit=200,
                exclude_archived=True
            )
        )

    return channels


def build_member_details(member_ids, all_users):
    return [
        {
            "id": user["id"],
            "name": user["name"],
            "real_name": user.get("real_name", "N/A"),
            "email": user["profile"].get("email", "N/A")
        }
        for uid in member_ids
        if (user := all_users.get(uid))
    ]
 

def get_channel_members(client, channel_id):
    return paginate(
        client.conversations_members,
        "members",
        channel=channel_id,
        limit=200
    )


def paginate(api_call, items_key, **kwargs):
    results = []
    cursor = None

    while True:
        response = api_call(cursor=cursor, **kwargs)
        results.extend(response[items_key])

        cursor = response.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break

    return results


def build_user(user_id, real_name=None, email=None):
    return {
        "id": user_id,
        "name":user_id,
        "real_name": real_name,
        "profile": {
            "email": email
        }
    }


def add_user_to_users(user,all_users):
      all_users[user["id"]]=user
