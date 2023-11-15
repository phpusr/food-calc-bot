from dataclasses import dataclass
from enum import Enum

from telebot import TeleBot


@dataclass
class Ingredient:
    name: str
    weight: float

    def __init__(self, ingredient_str: str):
        pair = ingredient_str.split(' ')
        self.name = pair[0].lower().capitalize()
        self.weight = float(pair[1])


class IWCStep(Enum):
    START = 1
    CLIENT_FOOD_WEIGHT = 2
    REST_FOOD_WEIGHT = 3
    INGREDIENTS = 4
    DONE = 5


@dataclass
class IngredientsWeightCalculator:
    bot: TeleBot
    step: IWCStep
    all_weight: float
    client_weight: float

    def __init__(self, bot):
        self.bot = bot
        self.step = IWCStep.START

    def next(self, message):
        match self.step:
            case IWCStep.START:
                self.bot.send_message(message.chat.id, 'Пупсик, введи массу своей доли, приготовленной еды')
                self.step = IWCStep.CLIENT_FOOD_WEIGHT
            case IWCStep.CLIENT_FOOD_WEIGHT:
                self.client_weight = float(message.text)
                self.bot.send_message(message.chat.id, 'Пупсик, введи массу оставшейся части, приготовленной еды')
                self.step = IWCStep.REST_FOOD_WEIGHT
            case IWCStep.REST_FOOD_WEIGHT:
                self.all_weight = self.client_weight + float(message.text)
                self.bot.send_message(message.chat.id, 'Пупсик, введи ингредиенты')
                self.step = IWCStep.INGREDIENTS
            case IWCStep.INGREDIENTS:
                result_message = self.calc_client_ingredients(message.text)
                self.bot.send_message(message.chat.id, result_message, 'Markdown')
                self.step = IWCStep.DONE
            case _:
                self.bot.send_message(message.chat.id, 'Wrong')

    def calc_client_ingredients(self, ingredients_str: str):
        ingredients = self.parse_ingredients(ingredients_str)
        client_part = self.client_weight / self.all_weight

        result_message = f'Твоя часть: {(client_part * 100):.1f}%\n\n'
        for ingredient in ingredients:
            client_ingredient_weight = ingredient.weight * client_part
            result_message += f'- {ingredient.name} - {client_ingredient_weight:.1f} г\n'

        return result_message

    def parse_ingredients(self, ingredients_str: str):
        ingredients = []
        for ingredient_str in ingredients_str.split('\n'):
            ingredients.append(Ingredient(ingredient_str))

        return ingredients

    def __str__(self):
        return self.step

