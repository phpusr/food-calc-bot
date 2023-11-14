import os
from dataclasses import dataclass

import telebot
from telebot import types


@dataclass
class Ingredient:
    name: str
    weight: int


@dataclass
class ContextData:
    step: str
    all_weight: int
    client_weight: int
    ingredients: list[Ingredient]

    def __init__(self, step: str):
        self.step = step

    def __str__(self):
        return self.step


def main():
    bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))
    context_data: dict[str, ContextData] = {}

    @bot.message_handler(commands=['start'])
    def start(message):
        markup = types.InlineKeyboardMarkup()
        start_calc_food = types.InlineKeyboardButton('Начать расчет', callback_data='start_calc')
        markup.add(start_calc_food)
        bot.send_message(message.from_user.id, "Приветики! 👋 Я твой бот-помощник по расчету еды!", reply_markup=markup)

    @bot.message_handler(commands=['start2'])
    def start_with_bottom_buttons(message):
        markup = types.ReplyKeyboardMarkup()
        start_calc_food = types.KeyboardButton('Начать расчет')
        markup.add(start_calc_food)
        bot.send_message(message.from_user.id, "Приветики! 👋 Я твой бот-помощник по расчету еды!", reply_markup=markup)

    @bot.message_handler(commands=['start_calc'])
    def start_calc(message):
        context_data[message.chat.id] = ContextData('start_calc')
        bot.send_message(message.chat.id, 'Введи общую массу приготовленной еды')

    @bot.callback_query_handler(func=lambda call: True)
    def callback_query(call):
        command = call.data

        if command == 'start_calc':
            context_data[call.message.chat.id] = ContextData(command)
            bot.edit_message_text('Введи общую массу приготовленной еды', call.message.chat.id, call.message.message_id)

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        message_text = message.text
        print('message:', message_text)
        context = context_data[message.chat.id]

        if context.step == 'start_calc':
            context.all_weight = int(message_text)
            context.step = 'ingredients'
            bot.send_message(message.from_user.id, 'Введи ингредиенты')
        elif context.step == 'ingredients':
            parse_ingredients(context, message_text)
            bot.send_message(message.from_user.id, 'Ингредиенты получены')
        elif message_text == '👋 Поздороваться':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            btn1 = types.KeyboardButton('Как стать автором на Хабре?')
            btn2 = types.KeyboardButton('Правила сайта')
            btn3 = types.KeyboardButton('Советы по оформлению публикации')
            markup.add(btn1, btn2, btn3)
            bot.send_message(message.from_user.id, '❓ Задайте интересующий вас вопрос', reply_markup=markup)
        elif message_text == 'Правила сайта':
            bot.send_message(message.from_user.id, 'Прочитать правила сайта вы можете по ' + '[ссылке](https://habr.com/ru/docs/help/rules/)', parse_mode='Markdown')
        else:
            bot.send_message(message.from_user.id, 'Не разобрал')

    def parse_ingredients(context: ContextData, ingredients_str: str):
        context.ingredients = []
        for ingredient in ingredients_str.split('\n'):
            print('-', ingredient)
            pair = ingredient.split(' ')
            context.ingredients.append(Ingredient(name=pair[0], weight=int(pair[1])))

    bot.polling(none_stop=True, interval=0)


if __name__ == '__main__':
    main()

