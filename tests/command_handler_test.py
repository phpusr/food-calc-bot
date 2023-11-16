from unittest import TestCase

from commands.ingredients_mass_calculator import IngredientsMassCalculator
from common.command_handler import BaseCommandHandler


class TestParser(TestCase):

    def test_message_text_handle(self):
        res_str = BaseCommandHandler._handle_message_text('   hello     everybody   ')
        self.assertEqual(res_str, 'hello everybody')

        res_str = BaseCommandHandler._handle_message_text('   juice      50   ')
        self.assertEqual(res_str, 'juice 50')

    def test_parse_ingredients(self):
        self._test_parse_ingredients('cheese 50\n\n', 'cheese 50.0')
        self._test_parse_ingredients('cheese 50\n juice  50', 'cheese 50.0,juice 50.0')
        self.assertRaises(ValueError, lambda: self._test_parse_ingredients('cheese 50\n juice 50 d', 'cheese 50.0,juice 50'))

    def _test_parse_ingredients(self, ingredients_str: str, result_str: str):
        ingredients_str = BaseCommandHandler._handle_message_text(ingredients_str)
        ingredient_list = [str(ingredient) for ingredient in IngredientsMassCalculator._parse_ingredients(ingredients_str)]
        ingredients = ','.join(ingredient_list)
        self.assertEqual(ingredients, result_str)
