import unittest
from unittest.mock import MagicMock, patch

from slack_sdk import WebClient
from slack_shevi.slack_client import paginate
from slack_shevi.users import get_slack_users, build_user, add_user_to_users
from slack_shevi.channels import (
    list_all_channels,
    get_channel_members,
    build_member_details,
    create_connection_list
)


class TestSlackClient(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()

    def test_paginate(self):
        def mock_api_call(cursor=None, **kwargs):
            if cursor is None:
                return {"items": [1, 2], "response_metadata": {"next_cursor": "abc"}}
            else:
                return {"items": [3], "response_metadata": {"next_cursor": ""}}

        results = paginate(mock_api_call, "items")
        self.assertEqual(results, [1, 2, 3])


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


class TestChannels(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()

    def test_list_all_channels(self):
        self.mock_client.conversations_list.side_effect = [
            {"channels": [{"id": "C1", "name": "general"}], "response_metadata": {"next_cursor": ""}},
            {"channels": [{"id": "G1", "name": "private"}], "response_metadata": {"next_cursor": ""}}
        ]
        channels = list_all_channels(self.mock_client)
        self.assertEqual(len(channels), 2)

    def test_get_channel_members(self):
        self.mock_client.conversations_members.return_value = {
            "members": ["U1", "U2"], "response_metadata": {"next_cursor": ""}
        }
        members = get_channel_members(self.mock_client, "C1")
        self.assertEqual(members, ["U1", "U2"])

    def test_build_member_details(self):
        all_users = {
            "U1": {"id": "U1", "name": "user1", "real_name": "User One", "profile": {"email": "u1@example.com"}},
            "U2": {"id": "U2", "name": "user2", "real_name": "User Two", "profile": {"email": "u2@example.com"}}
        }
        member_ids = ["U1", "U2"]
        details = build_member_details(member_ids, all_users)
        self.assertEqual(len(details), 2)
        self.assertEqual(details[0]["email"], "u1@example.com")

    @patch("slack_shevi.channels.list_all_channels")
    @patch("slack_shevi.channels.get_channel_members")
    @patch("slack_shevi.users.get_slack_users")
    def test_create_connection_list(
        self, mock_get_users, mock_get_members, mock_list_channels
    ):
        mock_list_channels.return_value = [{"id": "C1", "name": "general"}]
        mock_get_members.return_value = ["U1", "U2"]
        mock_get_users.return_value = {
            "U1": {"id": "U1", "name": "user1", "real_name": "User One", "profile": {"email": "u1@example.com"}},
            "U2": {"id": "U2", "name": "user2", "real_name": "User Two", "profile": {"email": "u2@example.com"}}
        }

        connection_list = create_connection_list(self.mock_client)
        self.assertIn("general", connection_list)
        self.assertEqual(len(connection_list["general"]), 2)
        self.assertEqual(connection_list["general"][0]["email"], "u1@example.com")


if __name__ == "__main__":
    unittest.main()
