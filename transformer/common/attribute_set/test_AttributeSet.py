from unittest import TestCase

from transformer.common.attribute_set.AttributeSet import AttributeSet
from transformer.common.attribute_set.metadata_updater.implementation.TestUpdaters import *
from transformer.common.dto.AttributeDto import Transmission


class TestAttributeSet(TestCase):



    def setUp(self) -> None:
        self.set = AttributeSet(updater=AlwaysRaises())

    def test_addNoConflict(self):
        transmission0 = Transmission(title="transmission0")
        self.assertTrue(self.set.add(transmission0), "add return value")
        expected = {transmission0}
        found = set(item for item in self.set)
        self.assertEqual(expected, found, "Set elements")





