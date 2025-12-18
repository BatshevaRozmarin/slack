import unittest
from unittest.mock import MagicMock

from slack_shevi.users import get_slack_users, build_user, add_user_to_users


class TestUsers(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()

    def test_get_slack_users(self):
        self.mock_client.users_list.return_value = {
            "members": [{"id": "U1", "name": "user1", "profile": {"email": "a@b.com"}}],
            "response_metadata": {"next_cursor": ""}
        }
        users = get_slack_users(self.mock_client)
        self.assertIn("U1", users)

    def test_build_and_add_user(self):
        user = build_user("U2", "Real Name", "email@example.com")
        all_users = {}
        add_user_to_users(user, all_users)
        self.assertIn("U2", all_users)
        self.assertEqual(all_users["U2"]["real_name"], "Real Name")

if __name__ == "__main__":
    unittest.main()
