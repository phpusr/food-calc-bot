import enum
import json
import os
from typing import Optional, Callable

from telebot import TeleBot, ExceptionHandler
from telebot.types import InlineKeyboardButton, BotCommand

from common.command_handler import BaseCommandHandler
from i18n import messages


class CommandInlineKeyboardMarkup(InlineKeyboardButton):
    def __init__(self, title: str, command_name: str):
        callback_data = json.dumps({'command': command_name})
        super().__init__(title, callback_data=callback_data)


class CustomExceptionHandler(ExceptionHandler):
    def handle(self, exception: Exception):
        print(f'Exception {exception.__class__.__name__}: {exception}')
        return True


@enum.unique
class BotCommandType(enum.Enum):
    START = 'start'


class BaseBot:
    debug = False
    change_name: bool
    name: str
    description: str
    allowed_users: list[str]
    context_data: dict[int, BaseCommandHandler]
    commands: list[BotCommand]

    def __init__(self):
        self.change_name = os.getenv('BOT_CHANGE_NAME') == 'TRUE'
        self.bot = TeleBot(os.getenv('BOT_TOKEN'), exception_handler=CustomExceptionHandler())
        self.allowed_users = os.getenv('BOT_ALLOWED_USERS', '').split(',')
        self.context_data = {}
        self.commands = []

        self.add_command_handler(
            handler=self.start_command,
            commands=[BotCommandType.START.value],
            description=messages.command_start_description
        )
        self.add_command_handlers()
        self.add_callback_query_handler(lambda call: True, self._callback_query)
        self.add_message_handler(self._text_messages_handler, content_types=['text'])

        if self.change_name and self.name:
            self.bot.set_my_name(self.name)
        if self.change_name and self.description:
            self.bot.set_my_description(self.description)
        self.bot.set_my_commands(self.commands)

    def start(self):
        self.bot.polling(none_stop=True, interval=0)

    def add_command_handlers(self):
        pass

    def start_command(self, message):
        self.print_help(message)

    def print_help(self, message):
        self.bot.send_message(message.from_user.id, messages.implement_me)

    def _callback_query(self, call):
        data = json.loads(call.data)
        command_name = data.get('command')
        if command_name:
            command_handler = getattr(self, f'{command_name}_command')
            self.bot.delete_message(call.message.chat.id, call.message.id)
            command_handler(call.message)

    def _text_messages_handler(self, message):
        if self.debug:
            print('message:', message.text)

        allowed = self.check_access_to_command(message)
        if not allowed:
            # If user wrote right answer then add him to allowed users
            if message.text.lower() == messages.i_am_sweeties:
                self.allowed_users.append(message.from_user.username)
                self.print_help(message)
            else:
                self.bot.send_message(message.chat.id, messages.access_denied)
            return

        context = self.context_data.get(message.chat.id)
        if context and context.step:
            try:
                context.next(message)
            except ValueError as e:
                if str(e).startswith('could not convert string to float'):
                    self.bot.send_message(message.chat.id, messages.error_float_convert)
                    return
                raise e
            return

        self.print_help(message)

    def add_command_handler(self, handler,
                            commands: list[str] = None,
                            regexp: str = None,
                            func: Callable = None,
                            content_types: list[str] = None,
                            chat_types: list[str] = None,
                            description: str = '',
                            **kwargs):

        if content_types is None:
            content_types = ['text']

        method_name = 'message_handler'

        if commands is not None:
            self.bot.check_commands_input(commands, method_name)
            if isinstance(commands, str):
                commands = [commands]

        if regexp is not None:
            self.bot.check_regexp_input(regexp, method_name)

        if isinstance(content_types, str):
            print('message_handler: "content_types" filter should be List of strings (content types), not string.')
            content_types = [content_types]

        for command in commands:
            self.commands.append(BotCommand(command, description))

        # noinspection PyProtectedMember
        handler_dict = self.bot._build_handler_dict(handler,
                                                    chat_types=chat_types,
                                                    content_types=content_types,
                                                    commands=commands,
                                                    regexp=regexp,
                                                    func=self.check_access_to_command,
                                                    **kwargs)
        self.bot.add_message_handler(handler_dict)

    def add_callback_query_handler(self, func, handler, **kwargs):
        # noinspection PyProtectedMember
        handler_dict = self.bot._build_handler_dict(handler, func=func, **kwargs)
        self.bot.callback_query_handlers.append(handler_dict)

    def add_message_handler(
                    self,
                    handler: Callable,
                    commands: Optional[list[str]] = None,
                    regexp: Optional[str] = None,
                    func: Optional[Callable] = None,
                    content_types: Optional[list[str]] = None,
                    chat_types: Optional[list[str]] = None,
                    **kwargs):

        if content_types is None:
            content_types = ['text']

        method_name = 'message_handler'

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

    def check_access_to_command(self, message):
        return message.from_user.username in self.allowed_users
