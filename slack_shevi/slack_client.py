import os
from dotenv import load_dotenv
from slack_sdk import WebClient

load_dotenv()

def get_slack_client():
    slack_token = os.environ.get("SLACK_BOT_TOKEN")
    if not slack_token:
        raise ValueError("SLACK_BOT_TOKEN environment variable not set.")
    return WebClient(token=slack_token)


def paginate(api_call, items_key: str, **kwargs):
    results = []
    cursor = None
    while True:
        response = api_call(cursor=cursor, **kwargs)
        results.extend(response[items_key])
        cursor = response.get("response_metadata", {}).get("next_cursor")
        if not cursor:
            break
    return results
