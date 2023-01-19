import datetime
from typing import *
from unittest import TestCase

from common.domain.entities import RawData
from extractor.scraper.ModelInfoScraper import ModelInfoScraper


# Minimal implementation of ModelInfoScraper for testing
class TestScraper(ModelInfoScraper):

    def __init__(self, brandName: str, manufacturerCommon: str, **kwargs):
        super().__init__(brandName=brandName, manufacturerCommon=manufacturerCommon, **kwargs)

    def fetchModelYear(self, date: 'datetime.date') -> List['RawData']:
        return list()

    def persistModelYear(self, date: 'datetime.date') -> None:
        return None

class TestModelInfoScraper(TestCase):

    testBrandName = 'Test Brand'
    testManufacturerCommon = 'Test Manufacturer'
    testScraper = TestScraper(brandName=testBrandName, manufacturerCommon=testManufacturerCommon)

    def test_getBrandName(self):
        self.assertEqual(self.testBrandName, self.testScraper.getBrandName() )

    def test_getManufacturerCommon(self):
        self.assertEqual(self.testManufacturerCommon, self.testScraper.getManufacturerCommon() )


    def test__validateModelYearDoesNotRaise(self):
        date = datetime.date(2022,1,1)
        self.assertIs(None, self.testScraper._validateModelYear(date) )

    def test__validateModelYearRaises(self):
        date = datetime.date(2022, 2, 1)
        self.assertRaises(ValueError, lambda: self.testScraper._validateModelYear(date))

