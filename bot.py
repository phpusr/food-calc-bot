import enum

from telebot import types

from commands.ingredients_weight_calculator import IngredientsWeightCalculator
from common.bot import BaseBot, CommandInlineKeyboardMarkup


@enum.unique
class FoodCalcBotCommand(enum.Enum):
    CALC_INGREDIENTS_WEIGHT = 'calc_ingredients_weight'


class FoodCalcBot(BaseBot):

    def add_command_handlers(self):
        self.add_command_handler(self.calc_ingredients_weight_command,
                                 [FoodCalcBotCommand.CALC_INGREDIENTS_WEIGHT.value])

    def print_help(self, message):
        markup = types.InlineKeyboardMarkup()
        start_calc_food = CommandInlineKeyboardMarkup('Начать расчет', FoodCalcBotCommand.CALC_INGREDIENTS_WEIGHT.value)
        markup.add(start_calc_food)
        self.bot.send_message(message.from_user.id, "Приветики, Пупсик 👋 Я твой бот-помощник по расчету еды!", reply_markup=markup)

    def calc_ingredients_weight_command(self, message):
        calculator = IngredientsWeightCalculator(self.bot)
        self.context_data[message.chat.id] = calculator
        calculator.next(message)

