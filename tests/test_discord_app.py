import pytest
from unittest.mock import MagicMock
import sys
import os

# Add the project root directory to the Python path to find 'src'
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.discord_app import bot_is_mentioned

mock_client_user = MagicMock()
mock_client_user.mention = "<@123456789>"

@pytest.mark.parametrize(
    "content, client_user, expected",
    [
        ("hey bot, what's up?", mock_client_user, True),
        ("Bot help me", mock_client_user, True),
        ("Can you help, bot?", mock_client_user, True),
        ("bot", mock_client_user, True),
        ("BOT", mock_client_user, True),
        ("<@123456789> hello", mock_client_user, True),
        ("Hello <@123456789>", mock_client_user, True),
        ("Ask the bot a question", mock_client_user, True),
        ("Both are good.", mock_client_user, False),
        ("This is about robotics", mock_client_user, False),
        ("Just a normal message", mock_client_user, False),
        ("The chatbot is useful", mock_client_user, False),
        ("", mock_client_user, False),
    ],
)
def test_is_bot_mentioned(content, client_user, expected):
    assert bot_is_mentioned(content, client_user) == expected
