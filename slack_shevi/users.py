from slack_shevi.slack_client import paginate


def get_slack_users(client):
    users = paginate(client.users_list, "members", limit=200)
    return {user["id"]: user for user in users}


def build_user(user_id: str, real_name: str = None, email: str = None):
    return {
        "id": user_id,
        "name": user_id,
        "real_name": real_name,
        "profile": {"email": email},
    }


def add_user_to_users(user: dict, all_users: dict):
    all_users[user["id"]] = user
