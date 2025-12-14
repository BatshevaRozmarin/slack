import json
import os
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
        public_channels = client.conversations_list(types="public_channel")
        if public_channels["ok"]:
            channels.extend(public_channels["channels"])
    except SlackApiError as e:
        print(f"Error fetching public channels: {e.response['error']}")

    try:
        private_channels = client.conversations_list(types="private_channel")
        if private_channels["ok"]:
            channels.extend(private_channels["channels"])
    except SlackApiError as e:
        print(f"Error fetching private channels: {e.response['error']}")
        
    return channels


def get_channel_members(client, channel_id):
    member_ids = []
    try:
        response = client.conversations_members(channel=channel_id)
        if response["ok"]:
            member_ids.extend(response["members"])
    except SlackApiError as e:
        print(f"Error fetching members for channel {channel_id}: {e.response['error']}")
    return member_ids


def get_user_details(client, user_id):
    try:
        response = client.users_info(user=user_id)
        if response["ok"]:
            return response["user"]
    except SlackApiError as e:
        print(f"Error fetching user details for {user_id}: {e.response['error']}")
    return None


if __name__ == '__main__':
    try:
        client = get_slack_client()
        full_list = create_connection_list(client)
        
        print(json.dumps(full_list, indent=4))
        
    except ValueError as e:
        print(e)
    except SlackApiError as e:
        print(f"A general Slack API error occurred: {e.response['error']}")
