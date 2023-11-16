import enum
from dataclasses import dataclass

from common.command_handler import BaseCommandHandler
from i18n import messages


@dataclass
class Ingredient:
    name: str
    mass: float

    def __init__(self, name: str, mass: float):
        self.name = name
        self.mass = mass

    def __str__(self):
        return f'{self.name} {self.mass}'


@enum.unique
class IWCStep(enum.Enum):
    START = 1
    CLIENT_FOOD_MASS = 2
    REST_FOOD_MASS = 3
    INGREDIENTS = 4


class IngredientsMassCalculator(BaseCommandHandler):
    step: IWCStep | None
    all_food_mass: float
    client_food_mass: float

    def __init__(self, bot):
        super().__init__(bot)
        self.step = IWCStep.START

    def _next(self):
        match self.step:
            case IWCStep.START:
                self.bot.send_message(self.chat_id, messages.iwc_enter_your_food_mass)
                self.step = IWCStep.CLIENT_FOOD_MASS
            case IWCStep.CLIENT_FOOD_MASS:
                self.client_food_mass = float(self.message_text)
                self.bot.send_message(self.chat_id, messages.iwc_enter_rest_food_mass)
                self.step = IWCStep.REST_FOOD_MASS
            case IWCStep.REST_FOOD_MASS:
                self.all_food_mass = self.client_food_mass + float(self.message_text)
                self.bot.send_message(self.chat_id, messages.iwc_enter_ingredients, 'Markdown')
                self.step = IWCStep.INGREDIENTS
            case IWCStep.INGREDIENTS:
                try:
                    result_message = self._calc_client_ingredients(self.message_text)
                except ValueError as e:
                    if str(e) == 'ingredients_parsing_error':
                        self.bot.send_message(self.chat_id, messages.iwc_error_parse_ingredients)
                        return
                    raise e

                self.bot.send_message(self.chat_id, result_message, 'Markdown')
                self.step = None
            case _:
                raise RuntimeError(f'step "{self.step}" isn\'t supported')

    def _calc_client_ingredients(self, ingredients_str: str):
        ingredients = self._parse_ingredients(ingredients_str)
        result_message = ''

        # Show warning if ingredients mass is much larger than food mass
        all_ingredients_mass = sum([ing.mass for ing in ingredients])
        diff_mass = round(all_ingredients_mass - self.all_food_mass)
        if diff_mass > 20:
            result_message += messages.iwc_warn_ingredients_mass.format(
                ingredients_mass=round(all_ingredients_mass), diff_mass=diff_mass)

        # Show list ingredients with mass
        client_part = self.client_food_mass / self.all_food_mass
        result_message += messages.iwc_client_part.format(client_part=client_part * 100)
        for ingredient in ingredients:
            client_ingredient_mass = ingredient.mass * client_part
            result_message += f'- {ingredient.name}: {client_ingredient_mass:.1f} г\n'

        result_message += messages.iwc_good_bye

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
