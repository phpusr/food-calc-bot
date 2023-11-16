from telebot import types

from commands.ingredients_weight_calculator import IngredientsWeightCalculator
from common.bot import BaseBot


class FoodCalcBot(BaseBot):

    def _add_command_handlers(self):
        self._add_command_handler(self.calc_ingredients_weight_command, ['calc_ingredients_weight'])

    def _start_command(self, message):
        markup = types.InlineKeyboardMarkup()
        start_calc_food = types.InlineKeyboardButton('Начать расчет', callback_data='calc_ingredients_weight')
        markup.add(start_calc_food)
        self.bot.send_message(message.from_user.id, "Приветики, Пупсик 👋 Я твой бот-помощник по расчету еды!", reply_markup=markup)

    def calc_ingredients_weight_command(self, message):
        calculator = IngredientsWeightCalculator(self.bot)
        self.context_data[message.chat.id] = calculator
        calculator.next(message)

    def _callback_query(self, call):
        if call.data == 'calc_ingredients_weight':
            self.bot.delete_message(call.message.chat.id, call.message.id)
            self.calc_ingredients_weight_command(call.message)
