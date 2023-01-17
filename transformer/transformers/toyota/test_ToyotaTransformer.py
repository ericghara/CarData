from unittest import TestCase

from common.domain.dto.AttributeDto import Accessory, Package, Engine
from transformer.transformers.toyota.ToyotaTransformer import ToyotaTransformer


class TestToyotaTransformer(TestCase):
    def setUp(self) -> None:
        self.transformer = ToyotaTransformer()
    
    def test__deDupAccessoryGrade(self):
        rawAttributes = [Accessory(title="Premium Package"), Package(title="Premium Package"), Engine(title="1ZZ")]
        foundAttributes = set(self.transformer._deDupAccessoryPackage(rawAttributes))
        expectedAttributes = {Package(title="Premium Package"), Engine(title="1ZZ")}
        self.assertEqual(expectedAttributes, foundAttributes)
        
