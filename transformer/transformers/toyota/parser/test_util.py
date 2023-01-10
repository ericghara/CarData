from unittest import TestCase

from parameterized import parameterized

from transformer.transformers.toyota.parser import util


class Test_Util(TestCase):

    @parameterized.expand([["$190", 190],
                           ["$0.00", 0],
                           ["$7,940", 7_940],
                           ["$1,000.99", 1_001],
                           [1_000.51, 1_001],
                           [1_000, 1_000]
                           ])
    def test_priceStrToInt(self, priceStr: str | int | float, expected: int):
        found = util.priceStrToInt(priceStr)
        self.assertEqual(expected, found)

    @parameterized.expand([["ALL-WEATHER FLOOR LINERS[FLOORMAT8]", "ALL-WEATHER FLOOR LINERS"],
                           ["TORSEN&reg;[TORSEN] LIMITED-SLIP REAR DIFFERENTIAL AND YAMAHA&reg",
                            "TORSEN&reg; LIMITED-SLIP REAR DIFFERENTIAL AND YAMAHA&reg"],
                           ["Not Bracketed[Bracketed], Not Bracketed[Bracketed].",
                            "Not Bracketed, Not Bracketed."]
                           ])
    def test_removeBracketed(self, bracketedText: str, expected: str):
        found = util.removeBracketed(bracketedText)
        self.assertEqual(expected, found)

    @parameterized.expand([
        ["$123.55", 123],
        ["153 Angry Cats", 153],
        [100, 100],
        [2.99, 3]
    ])
    def testDigitsToInt(self, input: str | int | float, expected: int):
        found = util.digitsToInt(input)
        self.assertEqual(expected, found)
