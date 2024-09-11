import unittest
import os
from src.message_logger import log_message
from unittest.mock import Mock

class TestMessageLogger(unittest.TestCase):
    def test_log_message(self):
        message = Mock()
        message.author = Mock()
        message.author.id = 123
        message.author.display_name = "TestUser"
        message.created_at = Mock()
        message.created_at.isoformat.return_value = "2024-01-01T00:00:00"
        message.content = "Hello World!"
        
        log_message(message)
        file_name = f"logs/{message.author}.json"
        self.assertTrue(os.path.exists(file_name))

if __name__ == '__main__':
    unittest.main()

