import enum

from telebot import types

from commands.ingredients_mass_calculator import IngredientsMassCalculator
from common.bot import BaseBot, CommandInlineKeyboardMarkup
from i18n import messages


@enum.unique
class FoodCalcBotCommand(enum.Enum):
    CALC_INGREDIENTS_MASS = 'calc_ingredients_mass'


class FoodCalcBot(BaseBot):
    name = messages.bot_name
    description = messages.bot_description

    def add_command_handlers(self):
        self.add_command_handler(
            handler=self.calc_ingredients_mass_command,
            commands=[FoodCalcBotCommand.CALC_INGREDIENTS_MASS.value],
            description=messages.command_calc_ingredients_mass
        )

    def print_help(self, message):
        markup = types.InlineKeyboardMarkup()
        calc_food_button = CommandInlineKeyboardMarkup(messages.calc_food_button_title,
                                                       FoodCalcBotCommand.CALC_INGREDIENTS_MASS.value)
        markup.add(calc_food_button)
        self.bot.send_message(message.from_user.id, messages.bot_help_message, reply_markup=markup)

    def calc_ingredients_mass_command(self, message):
        calculator = IngredientsMassCalculator(self.bot)
        self.context_data[message.chat.id] = calculator
        calculator.next(message)

