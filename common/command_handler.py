from enum import Enum

from telebot import TeleBot


class BaseCommandHandler:
    bot: TeleBot
    step: Enum

    def __init__(self, bot):
        self.bot = bot

    def next(self, message):
        try:
            self._next(message)
        except ValueError as e:
            if str(e).startswith('could not convert string to float'):
                self.bot.send_message(message.chat.id, 'Не могу преобразовать введенное в строку')
                return
            print(e)

    def _next(self, message):
        raise RuntimeError('Implement me')

    def parse_float(self, str_value: str):
        try:
            return float(str_value)
        except:
            pass
