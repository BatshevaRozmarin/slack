import unittest
from unittest.mock import MagicMock, patch
import json
from slack_sdk.errors import SlackApiError
from connection_list import list_all_channels, get_channel_members, get_user_details, create_connection_list

class TestSlackConnectionList(unittest.TestCase):

    def setUp(self):
        self.mock_client = MagicMock()

    @patch('connection_list.get_slack_client')
    def test_list_all_channels(self, mock_get_client):
        mock_get_client.return_value = self.mock_client
        
        self.mock_client.conversations_list.side_effect = [
            {"ok": True, "channels": [{"id": "C1", "name": "general"}]},
            {"ok": True, "channels": [{"id": "G1", "name": "private"}]}
        ]

        channels = list_all_channels(self.mock_client)
        self.assertEqual(len(channels), 2)
        self.assertEqual(channels[0]['name'], 'general')
        self.assertEqual(channels[1]['name'], 'private')

    def test_get_channel_members(self):
        self.mock_client.conversations_members.return_value = {
            "ok": True,
            "members": ["U1", "U2"]
        }
        members = get_channel_members(self.mock_client, "C1")
        self.assertEqual(members, ["U1", "U2"])

    def test_get_user_details(self):
        user_data = {
            "id": "U1",
            "name": "john_doe",
            "real_name": "John Doe",
            "profile": {"email": "john.doe@example.com"}
        }
        self.mock_client.users_info.return_value = {
            "ok": True,
            "user": user_data
        }
        details = get_user_details(self.mock_client, "U1")
        self.assertEqual(details['name'], 'john_doe')
        self.assertEqual(details['profile']['email'], 'john.doe@example.com')

    @patch('connection_list.list_all_channels')
    @patch('connection_list.get_channel_members')
    @patch('connection_list.get_user_details')
    def test_create_connection_list(self, mock_get_user_details, mock_get_channel_members, mock_list_channels):
        
        mock_list_channels.return_value = [{"id": "C1", "name": "general"}]
        mock_get_channel_members.return_value = ["U1", "U2"]
        
        mock_get_user_details.side_effect = [
            {"id": "U1", "name": "user1", "real_name": "User One", "profile": {"email": "user1@example.com"}},
            {"id": "U2", "name": "user2", "real_name": "User Two", "profile": {"email": "user2@example.com"}}
        ]

        connection_list = create_connection_list(self.mock_client)
        
        self.assertIn('general', connection_list)
        self.assertEqual(len(connection_list['general']), 2)
        self.assertEqual(connection_list['general'][0]['email'], 'user1@example.com')
        self.assertEqual(connection_list['general'][1]['email'], 'user2@example.com')

if __name__ == '__main__':
    unittest.main()
