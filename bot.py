import os
from typing import Optional, Callable

from telebot import TeleBot, types

from commands.ingredients_weight_calculator import IngredientsWeightCalculator


class FoodCalcBot:
    context_data: dict[str, IngredientsWeightCalculator] = {}

    def __init__(self):
        self.bot = TeleBot(os.getenv('BOT_TOKEN'))
        self._add_command_handler(self.start_command, ['start'])
        self._add_command_handler(self.calc_ingredients_weight_command, ['calc_ingredients_weight'])
        self._add_callback_query_handler(lambda call: True, self.callback_query)
        self._add_message_handler(self.get_text_messages, content_types=['text'])

    def start(self):
        self.bot.polling(none_stop=True, interval=0)

    def start_command(self, message):
        markup = types.InlineKeyboardMarkup()
        start_calc_food = types.InlineKeyboardButton('Начать расчет', callback_data='calc_ingredients_weight')
        markup.add(start_calc_food)
        self.bot.send_message(message.from_user.id, "Приветики! 👋 Я твой бот-помощник по расчету еды!", reply_markup=markup)

    def calc_ingredients_weight_command(self, message):
        calculator = IngredientsWeightCalculator(self.bot)
        self.context_data[message.chat.id] = calculator
        calculator.next(message)

    def callback_query(self, call):
        command = call.data
        if command == 'calc_ingredients_weight':
            self.bot.delete_message(call.message.chat.id, call.message.id)
            self.calc_ingredients_weight_command(call.message)

    def get_text_messages(self, message):
        message_text = message.text
        print('message:', message_text)
        context = self.context_data[message.chat.id]

        if context:
            context.next(message)
        else:
            self.bot.send_message(message.chat.id, 'Не разобрал')

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
