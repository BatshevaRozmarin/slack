from slack_sdk import WebClient

from slack_shevi.slack_client import paginate
from slack_shevi.users import get_slack_users

def create_connection_list(client: WebClient):
    all_users = get_slack_users(client)
    if not all_users:
        raise ValueError("No users found in Slack workspace.")
    return {
        channel.get("name", "N/A"): build_member_details(
            get_channel_members(client, channel["id"]),
            all_users
        )
        for channel in list_all_channels(client)
    }


def list_all_channels(client: WebClient, channel_types=("public_channel", "private_channel")):
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


def get_channel_members(client: WebClient, channel_id: str):
    return paginate(client.conversations_members, "members", channel=channel_id, limit=200)


def build_member_details(member_ids: list, all_users: dict):
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
