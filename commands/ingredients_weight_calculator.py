import enum
from dataclasses import dataclass

from common.command_handler import BaseCommandHandler


@dataclass
class Ingredient:
    name: str
    weight: float

    def __init__(self, name: str, weight: float):
        self.name = name
        self.weight = weight

    def __str__(self):
        return f'{self.name} {self.weight}'


@enum.unique
class IWCStep(enum.Enum):
    START = 1
    CLIENT_FOOD_WEIGHT = 2
    REST_FOOD_WEIGHT = 3
    INGREDIENTS = 4


class IngredientsWeightCalculator(BaseCommandHandler):
    step: IWCStep | None
    all_weight: float
    client_weight: float

    def __init__(self, bot):
        super().__init__(bot)
        self.step = IWCStep.START

    def _next(self):
        match self.step:
            case IWCStep.START:
                self.bot.send_message(self.chat_id, 'Пупсик, введи массу своей доли, приготовленной еды')
                self.step = IWCStep.CLIENT_FOOD_WEIGHT
            case IWCStep.CLIENT_FOOD_WEIGHT:
                self.client_weight = float(self.message_text)
                self.bot.send_message(self.chat_id, 'Пупсик, введи массу оставшейся части, приготовленной еды')
                self.step = IWCStep.REST_FOOD_WEIGHT
            case IWCStep.REST_FOOD_WEIGHT:
                self.all_weight = self.client_weight + float(self.message_text)
                self.bot.send_message(self.chat_id, 'Пупсик, введи ингредиенты и их массу\n\nПример:\n\n'
                                                       'курица 90\nсыр 30\nсметана 20')
                self.step = IWCStep.INGREDIENTS
            case IWCStep.INGREDIENTS:
                try:
                    result_message = self._calc_client_ingredients(self.message_text)
                except ValueError as e:
                    if str(e) == 'ingredients_parsing_error':
                        self.bot.send_message(self.chat_id, 'Не смог понять твой список, попробуй еще раз, смотри пример')
                        return
                    raise e

                self.bot.send_message(self.chat_id, result_message, 'Markdown')
                self.step = None
            case _:
                raise RuntimeError(f'step "{self.step}" isn\'t supported')

    def _calc_client_ingredients(self, ingredients_str: str):
        ingredients = self._parse_ingredients(ingredients_str)
        client_part = self.client_weight / self.all_weight
        all_ingredients_weight = 0

        result_message = f'Твоя часть: {(client_part * 100):.1f}%\n\n'
        for ingredient in ingredients:
            all_ingredients_weight += ingredient.weight
            diff_weight = round(all_ingredients_weight - self.all_weight)
            if diff_weight > 20:
                result_message += (f'Масса всех ингредиентов *{round(all_ingredients_weight)}г* '
                                   f'превышает массу приготовленной еды на *{diff_weight}г*\n\n')

            client_ingredient_weight = ingredient.weight * client_part
            result_message += f'- {ingredient.name}: {client_ingredient_weight:.1f} г\n'

        return result_message

    @staticmethod
    def _parse_ingredients(ingredients_str: str) -> list[Ingredient]:
        ingredients = []
        for ingredient_str in ingredients_str.split('\n'):
            ingredient_str = ingredient_str.strip()
            if not ingredient_str:
                continue

            pair = ingredient_str.split(' ')
            if len(pair) != 2:
                raise ValueError('ingredients_parsing_error')

            ingredients.append(Ingredient(pair[0], float(pair[1])))

        return ingredients
