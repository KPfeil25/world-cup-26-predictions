import unittest
from src.add_nums import add_nums

class TestAddNums(unittest.TestCase):
    def test_one_shot_case_one(self):
        num1 = 5
        num2 = 10
        result = add_nums(5,10)
        self.assertEqual(result, 15)