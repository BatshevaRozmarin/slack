import unittest
from unittest.mock import MagicMock, patch

from slack_shevi.channels import (
    create_connection_list,
    get_channel_members,
    list_all_channels,
)


class TestSlackConnectionList(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()

    def test_list_all_channels(self):
        self.mock_client.conversations_list.side_effect = [
            {
                "channels": [{"id": "C1", "name": "general"}],
                "response_metadata": {"next_cursor": ""}
            },
            {
                "channels": [{"id": "G1", "name": "private"}],
                "response_metadata": {"next_cursor": ""}
            }
        ]

        channels = list_all_channels(self.mock_client)

        self.assertEqual(len(channels), 2)
        self.assertEqual(channels[0]["name"], "general")
        self.assertEqual(channels[1]["name"], "private")

    def test_get_channel_members(self):
        self.mock_client.conversations_members.return_value = {
            "members": ["U1", "U2"],
            "response_metadata": {"next_cursor": ""}
        }

        members = get_channel_members(self.mock_client, "C1")
        self.assertEqual(members, ["U1", "U2"])

    @patch("slack_shevi.channels.list_all_channels")
    @patch("slack_shevi.channels.get_channel_members")
    @patch("slack_shevi.channels.get_slack_users")
    def test_create_connection_list(
        self,
        mock_get_slack_users,
        mock_get_channel_members,
        mock_list_channels
    ):
        mock_list_channels.return_value = [
            {"id": "C1", "name": "general"}
        ]

        mock_get_channel_members.return_value = ["U1", "U2"]

        mock_get_slack_users.return_value = {
            "U1": {
                "id": "U1",
                "name": "user1",
                "real_name": "User One",
                "profile": {"email": "user1@example.com"}
            },
            "U2": {
                "id": "U2",
                "name": "user2",
                "real_name": "User Two",
                "profile": {"email": "user2@example.com"}
            }
        }

        connection_list = create_connection_list(self.mock_client)

        self.assertIn("general", connection_list)
        self.assertEqual(len(connection_list["general"]), 2)
        self.assertEqual(
            connection_list["general"][0]["email"],
            "user1@example.com"
        )
        self.assertEqual(
            connection_list["general"][1]["email"],
            "user2@example.com"
        )


if __name__ == "__main__":
    unittest.main()
