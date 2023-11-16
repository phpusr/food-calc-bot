from unittest import TestCase

from common.command_handler import BaseCommandHandler


class TestParser(TestCase):

    def test_message_text_handle(self):
        handler = BaseCommandHandler(None)

        res_str = handler._handle_message_text('   hello     everybody   ')
        self.assertEqual(res_str, 'hello everybody')

        res_str = handler._handle_message_text('   juice      50   ')
        self.assertEqual(res_str, 'juice 50')
