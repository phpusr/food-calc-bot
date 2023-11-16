from enum import Enum

from telebot import TeleBot


class BaseCommandHandler:
    bot: TeleBot
    step: Enum
    message: any
    message_text: str

    def __init__(self, bot):
        self.bot = bot

    def next(self, message):
        self.message = message
        self.message_text = self._handle_message_text(message.text)
        self._next()

    def _next(self):
        raise RuntimeError('Implement me')

    @property
    def chat_id(self):
        return self.message.chat.id

    @staticmethod
    def _handle_message_text(text: str) -> str:
        new_text = text.strip()
        while '  ' in new_text:
            new_text = new_text.replace('  ', ' ')
        return new_text
