import enum

from telebot import types

from commands.ingredients_weight_calculator import IngredientsWeightCalculator
from common.bot import BaseBot, CommandInlineKeyboardMarkup
from i18n import messages


@enum.unique
class FoodCalcBotCommand(enum.Enum):
    CALC_INGREDIENTS_WEIGHT = 'calc_ingredients_weight'


class FoodCalcBot(BaseBot):
    name = messages.bot_name
    description = messages.bot_description

    def add_command_handlers(self):
        self.add_command_handler(
            handler=self.calc_ingredients_weight_command,
            commands=[FoodCalcBotCommand.CALC_INGREDIENTS_WEIGHT.value],
            description=messages.command_calc_ingredients_weight
        )

    def print_help(self, message):
        markup = types.InlineKeyboardMarkup()
        calc_food_button = CommandInlineKeyboardMarkup(messages.calc_food_button_title,
                                                       FoodCalcBotCommand.CALC_INGREDIENTS_WEIGHT.value)
        markup.add(calc_food_button)
        self.bot.send_message(message.from_user.id, messages.bot_help_message, reply_markup=markup)

    def calc_ingredients_weight_command(self, message):
        calculator = IngredientsWeightCalculator(self.bot)
        self.context_data[message.chat.id] = calculator
        calculator.next(message)

