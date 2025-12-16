import json
import os
import sys

from dotenv import load_dotenv
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


load_dotenv()

def get_slack_client():
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    if not slack_token:
        raise ValueError("SLACK_API_TOKEN environment variable not set.")
    return WebClient(token=slack_token)


def create_connection_list(client):
    channels = list_all_channels(client)
    connection_list = {}

    for channel in channels:
        channel_id = channel['id']
        channel_name = channel.get('name', 'N/A')
        members = get_channel_members(client, channel_id)
        member_details_list = []

        for member_id in members:
            user_detail = get_user_details(client, member_id)
            if user_detail:
                member_details_list.append({
                    'id': user_detail['id'],
                    'name': user_detail['name'],
                    'real_name': user_detail.get('real_name', 'N/A'),
                    'email': user_detail['profile'].get('email', 'N/A')
                })
        
        connection_list[channel_name] = member_details_list
    
    return connection_list


def list_all_channels(client):
    channels = []

    try:
        for channel_type in ("public_channel", "private_channel"):
            response = client.conversations_list(types=channel_type)
            if response.get("ok"):
                channels.extend(response["channels"])

    except SlackApiError as e:
        raise RuntimeError(f"Error fetching channels: {e.response['error']}")

    return channels


def get_channel_members(client, channel_id):
    member_ids = []
    try:
        response = client.conversations_members(channel=channel_id)
        if response["ok"]:
            member_ids.extend(response["members"])
    except SlackApiError as e:
        raise RuntimeError(f"Error fetching members for channel {channel_id}: {e.response['error']}")
    return member_ids


def get_user_details(client, user_id):
    try:
        response = client.users_info(user=user_id)
        if response["ok"]:
            return response["user"]
    except SlackApiError as e:
        raise RuntimeError(f"Error fetching user details for {user_id}: {e.response['error']}")


def create_user(user_id, real_name=None, email=None):
    return {
        "id": user_id,
        "real_name": real_name,
        "email": email,
    }


def get_slack_users(client):
    users_map = {}
    try:
        response = client.users_list(limit=200)
        if response["ok"]:
            for user in response["members"]:
                users_map[user["id"]] = user

            return users_map
        
    except SlackApiError as e:
         raise RuntimeError(f"Error connecting to Slack API: {e.response['error']}")


def add_user(user,all_users):
      all_users[user["id"]]=user


if __name__ == '__main__':
    try:
        client = get_slack_client()
        full_list = create_connection_list(client)
        if len(sys.argv) == 4:
            user_id = sys.argv[1]
            user_name = sys.argv[2]
            user_email = sys.argv[3]

            user = create_user(user_id,user_name,user_email)
            all_users = get_slack_users(client)
            add_user(user,all_users)

        print(json.dumps(full_list, indent=4))
        
    except ValueError as e:
        raise RuntimeError(e)
    except SlackApiError as e:
        raise RuntimeError(f"A general Slack API error occurred: {e.response['error']}")
