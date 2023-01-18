from unittest import TestCase

from common.domain.dto.AttributeDto import Transmission, Engine
from common.domain.enum.MetadataType import MetadataType
from transformer.domain.attribute_set.AttributeSet import AttributeSet
from transformer.domain.attribute_set.metadata_updater.implementation.TestUpdaters import *


class TestAttributeSet(TestCase):

    def setUp(self) -> None:
        self.set = AttributeSet(updater=AlwaysRaises())

    def test_addNoConflict(self):
        transmission0 = Transmission(title="transmission0")
        self.assertTrue(self.set.add(transmission0), "add return value")
        expected = {transmission0}
        found = set(self.set)
        self.assertEqual(expected, found, "Set elements")

    def test_addConflictUpdates(self):
        self.set.updater = AlwaysUpdates()
        transmission0 = Transmission(title="transmission0")
        transmission1 = Transmission(title="transmission0",
                                     metadata=[AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=0)])
        self.set.add(transmission0)
        self.assertTrue(self.set.add(transmission1), "added transmission with metadata")
        expected = {transmission1}
        found = set(self.set)
        self.assertEqual(expected, found, "Set contents as expected")

    def test_addConflictNoUpdate(self):
        self.set.updater = NeverUpdates()
        transmission0 = Transmission(title="transmission0")
        transmission1 = Transmission(title="transmission0",
                                     metadata=[AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=0)])
        self.set.add(transmission0)
        self.assertFalse(self.set.add(transmission1), "On Conflict, no update should occur")
        expected = {transmission0}
        found = set(self.set)
        self.assertEqual(expected, found)

    def test_addMultipleNoConflict(self):
        transmission0 = Transmission(title="attribute")
        engine0 = Engine(title="attribute")
        self.set.add(transmission0)
        self.assertTrue(self.set.add(engine0))
        expected = {transmission0, engine0}
        found = set(self.set)
        self.assertEqual(expected, found)

    def test___len__(self):
        self.assertEqual(0, len(self.set), "Empty set returns 0" )
        transmission0 = Transmission(title="transmission0")
        self.set.add(transmission0)
        self.assertEqual(1, len(self.set), "Set with 1 element returns 1")

    def test___getitem__(self):
        transmission0 = Transmission(title="transmission0",
                                     metadata=[AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=0)])
        self.set.add(transmission0)
        self.assertEqual(transmission0.metadata, self.set[Transmission(title="transmission0")])

    def test___contains__(self):
        transmission0 = Transmission(title="transmission0",
                                     metadata=[AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=0)])
        self.set.add(transmission0)
        self.assertTrue(Transmission(title="transmission0") in self.set)

