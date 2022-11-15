from unittest import TestCase

from extractor.ModelInfoScraper import ModelInfoScraper
from repository.Entities import Brand, RawData
from unittest import mock
from typing import *
import datetime
from uuid import uuid4

# Minimal implementation of ModelInfoScraper for testing
class TestScraper(ModelInfoScraper):

    def __init__(self, brand: 'Brand', **kwargs):
        super().__init__(brand, **kwargs)

    def _fetchModelYear(self, date: 'datetime.date' ) -> List['RawData']:
        return list()

    def persistModelYear(self, date: 'datetime.date') -> None:
        return None

class TestModelInfoScraper(TestCase):

    testScraper = None
    testBrand = Brand(name='Test Brand')

    def test_queryBrandInfoNormalNoBrandId(self):
        fetchedBrand = Brand(brand_id=uuid4(), manufacturer_id=uuid4(), name=self.testBrand.name)
        with mock.patch('extractor.ModelInfoScraper.brandService.getBrandByName', return_value=fetchedBrand ):
            testScraper = TestScraper(self.testBrand)
            self.assertEquals(testScraper.brand, fetchedBrand)

    def test_queryBrandInfoNormalBrandIdMatches(self):
        brand = Brand(name='Test Brand', brand_id=uuid4() )
        fetchedBrand = Brand(brand_id=brand.brand_id, manufacturer_id=uuid4(), name=self.testBrand.name)
        with mock.patch('extractor.ModelInfoScraper.brandService.getBrandByName', return_value=fetchedBrand):
            testScraper = TestScraper(brand)
            self.assertEquals(testScraper.brand, fetchedBrand)

    def test_queryBrandInfoNromalBrandIdMisMatch(self):
        brand = Brand(name='Test Brand', brand_id=uuid4() )
        fetchedBrand = Brand(brand_id=uuid4(), manufacturer_id=uuid4(), name=self.testBrand.name)
        with mock.patch('extractor.ModelInfoScraper.brandService.getBrandByName', return_value=fetchedBrand):
            self.assertRaises(ValueError, lambda: TestScraper(brand) )

    def test__validateModelYearDoesNotRaise(self):
        date = datetime.date(2022,1,1)
        testScraper = TestScraper(self.testBrand, noPersist=True)
        self.assertIs(None, testScraper._validateModelYear(date) )

    def test__validateModelYearRaises(self):
        date = datetime.date(2022, 2, 1)
        testScraper = TestScraper(self.testBrand, noPersist=True)
        self.assertRaises(ValueError, lambda: testScraper._validateModelYear(date))

