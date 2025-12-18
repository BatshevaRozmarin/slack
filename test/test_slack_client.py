import unittest
from unittest.mock import MagicMock

from slack_shevi.slack_client import paginate


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

if __name__ == "__main__":
    unittest.main()
