from dataclasses import dataclass
from enum import Enum

from telebot import TeleBot


@dataclass
class Ingredient:
    name: str
    weight: int


class IWCStep(Enum):
    START = 1
    CLIENT_FOOD_WEIGHT = 2
    INGREDIENTS = 3


@dataclass
class IngredientsWeightCalculator:
    bot: TeleBot
    step: IWCStep
    all_weight: int
    client_weight: int
    ingredients: list[Ingredient]

    def __init__(self, bot):
        self.bot = bot
        self.step = IWCStep.START

    def next(self, message):
        match self.step:
            case IWCStep.START:
                self.bot.send_message(message.chat.id, 'Введи общую массу приготовленной еды')
                self.step = IWCStep.CLIENT_FOOD_WEIGHT
            case IWCStep.CLIENT_FOOD_WEIGHT:
                self.client_weight = int(message.text)
                self.bot.send_message(message.chat.id, 'Введи ингредиенты')
                self.step = IWCStep.INGREDIENTS
            case IWCStep.INGREDIENTS:
                self.parse_ingredients(message.text)
                self.bot.send_message(message.chat.id, 'Done')
            case _:
                self.bot.send_message(message.chat.id, 'Wrong')

    def parse_ingredients(self, ingredients_str: str):
        self.ingredients = []
        for ingredient in ingredients_str.split('\n'):
            print('-', ingredient)
            pair = ingredient.split(' ')
            ingredient = Ingredient(name=pair[0], weight=int(pair[1]))
            self.ingredients.append(ingredient)

    def __str__(self):
        return self.step

