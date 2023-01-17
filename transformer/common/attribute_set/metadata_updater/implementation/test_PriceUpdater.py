from typing import Optional, List
from unittest import TestCase

from parameterized import parameterized

from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from transformer.common.attribute_set.metadata_updater.implementation.PriceUpdater import PriceUpdater


class TestPriceUpdater(TestCase):

    def setUp(self):
        self.updater = PriceUpdater(metadataType=MetadataType.COMMON_MSRP, keepLowest=True)

    @parameterized.expand([([AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=0)], None, False),
                           (None, [AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=0)], True),
                           (None, None, False)])
    def test_updateNullHandling(self, old: Optional[List[AttributeMetadata]], new: Optional[List[AttributeMetadata]],
                                expected: bool):
        self.assertEqual(expected, self.updater.update(old, new))

    def test_updateRaisesOnDuplicatePrice(self):
        old = None
        new = [AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=0),
               AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=100)]
        self.assertRaises(ValueError, lambda: self.updater.update(old, new))

    def test_updateRaisesOnNullNewPrice(self):
        old = [AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=0)]
        new = [AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=None)]
        self.assertRaises(ValueError, lambda: self.updater.update(old, new))

    def testUpdateReturnsExpectedOnCompetingPricesLowest(self):
        old = [AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=0)]
        new = [AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=100)]
        self.assertFalse(self.updater.update(old, new))

    def testUpdateReturnsExpectedOnCompetingPricesHighest(self):
        self.updater.shouldUpdate = self.updater._keepHighest
        old = [AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=0)]
        new = [AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=100)]
        self.assertTrue(self.updater.update(old, new))

    def testUpdaterNoUpdateOnNoPriceMetadata(self):
        old = [AttributeMetadata(metadataType=MetadataType.BODY_STYLE_CAB, value="Double Cab")]
        new = [AttributeMetadata(metadataType=MetadataType.BODY_STYLE_CAB, value="Standard Cab")]
        self.assertFalse(self.updater.update(old,new))

    def testUpdaterUpdateOnOldNoPriceNewPrice(self):
        old = [AttributeMetadata(metadataType=MetadataType.BODY_STYLE_CAB, value="Standard Cab")]
        new = [AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=0)]
        self.assertTrue(self.updater.update(old,new))

    def testUpdaterNoUpdateOnOldPriceNoNewPrice(self):
        old = [AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=0)]
        new = [AttributeMetadata(metadataType=MetadataType.BODY_STYLE_CAB, value="Standard Cab")]
        self.assertFalse(self.updater.update(old,new))