import os
from typing import Optional, Callable

from telebot import TeleBot, ExceptionHandler

from common.command_handler import BaseCommandHandler


class CustomExceptionHandler(ExceptionHandler):
    def handle(self, exception: Exception):
        print(f'Exception {exception.__class__.__name__}: {exception}')
        return True


class BaseBot:
    context_data: dict[int, BaseCommandHandler]

    def __init__(self):
        self.bot = TeleBot(os.getenv('BOT_TOKEN'), exception_handler=CustomExceptionHandler())
        self.context_data = {}
        self._add_command_handlers()
        self._add_command_handler(self._start_command, ['start'])
        self._add_callback_query_handler(lambda call: True, self._callback_query)
        self._add_message_handler(self._get_text_messages, content_types=['text'])

    def start(self):
        self.bot.polling(none_stop=True, interval=0)

    def _add_command_handlers(self):
        pass

    def _start_command(self, message):
        self.bot.send_message(message.from_user.id, 'Implement me')

    def _callback_query(self, call):
        command = call.data
        print(command)

    def _get_text_messages(self, message):
        message_text = message.text
        print('message:', message_text)
        context = self.context_data.get(message.chat.id)

        if not context:
            self.bot.send_message(message.chat.id, 'Я не понял, выбери команду из списка')
            return

        try:
            context.next(message)
        except ValueError as e:
            if str(e).startswith('could not convert string to float'):
                self.bot.send_message(message.chat.id, 'Не могу преобразовать введенное в число')
                return
            print(e)

    def _add_command_handler(self, handler,
                             commands: Optional[list[str]] = None,
                             regexp: Optional[str] = None,
                             func: Optional[Callable] = None,
                             content_types: Optional[list[str]] = None,
                             chat_types: Optional[list[str]] = None,
                             **kwargs):

        if content_types is None:
            content_types = ["text"]

        method_name = "message_handler"

        if commands is not None:
            self.bot.check_commands_input(commands, method_name)
            if isinstance(commands, str):
                commands = [commands]

        if regexp is not None:
            self.bot.check_regexp_input(regexp, method_name)

        if isinstance(content_types, str):
            print("message_handler: 'content_types' filter should be List of strings (content types), not string.")
            content_types = [content_types]

        # noinspection PyProtectedMember
        handler_dict = self.bot._build_handler_dict(handler,
                                                    chat_types=chat_types,
                                                    content_types=content_types,
                                                    commands=commands,
                                                    regexp=regexp,
                                                    func=func,
                                                    **kwargs)
        self.bot.add_message_handler(handler_dict)

    def _add_callback_query_handler(self, func, handler, **kwargs):
        # noinspection PyProtectedMember
        handler_dict = self.bot._build_handler_dict(handler, func=func, **kwargs)
        self.bot.callback_query_handlers.append(handler_dict)

    def _add_message_handler(
                    self,
                    handler: Callable,
                    commands: Optional[list[str]] = None,
                    regexp: Optional[str] = None,
                    func: Optional[Callable] = None,
                    content_types: Optional[list[str]] = None,
                    chat_types: Optional[list[str]] = None,
                    **kwargs):

        if content_types is None:
            content_types = ["text"]

        method_name = "message_handler"

        if commands is not None:
            self.bot.check_commands_input(commands, method_name)
            if isinstance(commands, str):
                commands = [commands]

        if regexp is not None:
            self.bot.check_regexp_input(regexp, method_name)

        if isinstance(content_types, str):
            print('message_handler: "content_types" filter should be List of strings (content types), not string.')
            content_types = [content_types]

        # noinspection PyProtectedMember
        handler_dict = self.bot._build_handler_dict(handler,
                                                    chat_types=chat_types,
                                                    content_types=content_types,
                                                    commands=commands,
                                                    regexp=regexp,
                                                    func=func,
                                                    **kwargs)
        self.bot.add_message_handler(handler_dict)
