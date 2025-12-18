import json
import sys

from slack_sdk.errors import SlackApiError

from slack_shevi.channels import create_connection_list
from slack_shevi.slack_client import get_slack_client
from slack_shevi.users import (get_slack_users, build_user, add_user_to_users)

    
def main():
    try:
        client = get_slack_client()
        full_list = create_connection_list(client)
        if len(sys.argv[1:]) == 3:
            user_id = sys.argv[1]
            user_name = sys.argv[2]
            user_email = sys.argv[3]

            user = build_user(user_id, user_name, user_email)
            all_users = get_slack_users(client)
            add_user_to_users(user, all_users)
            print(all_users)

        print(json.dumps(full_list, indent=4))
        
    except ValueError as e:
        raise RuntimeError(e)
    except SlackApiError as e:
        raise RuntimeError(f"A general Slack API error occurred: {e.response['error']}")
    
if __name__ == '__main__':
    main()
