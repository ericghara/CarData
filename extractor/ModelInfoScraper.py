from typing import *
from abc import ABC, abstractmethod
from abc import ABCMeta
from repository.Entities import Brand, RawData
from datetime import date
from repository.SessionFactory import sessionFactory
from service.BrandService import brandService


# kwargs:
#   - noPersist: True/False
#       for testing, don't check that provided brand is a valid db record
class ModelInfoScraper(ABC):

    def __init__(self, brand: 'Brand', **kwargs):
        super().__init__()
        self.noPersist = kwargs.get('noPersist', False)
        self.brand = self.queryBrandInfo(brand)


    # When noPersist=False, only required info in brand obj is Name, if brand_id is not null
    # the provided brand_id will be validated against the fetched brand
    # if noPersist=True, the provided Brand object is simply returned
    def queryBrandInfo(self, brand: 'Brand') -> 'Brand':
        if self.noPersist:
            return brand
        fetchedBrand = brandService.getBrandByName(brand.name, sessionFactory.newSession() )
        if not fetchedBrand:
            raise ValueError(f'No record found for Brand: {brand.name}')
        if (brand.brand_id and brand.brand_id != fetchedBrand.brand_id):
            raise ValueError(f'Provided brand_id and fetched brand_id do not match')
        return fetchedBrand

    def _validateModelYear(self, date: 'date') -> None:
        if (date.month != 1 or date.day != 1 ):
            # override for manufacturers with multiple releases, ex. semi-annual
            raise ValueError(f'Month and day must be January 1st.')

    @abstractmethod
    def _fetchModelYear(self, date: 'date' ) -> dict[str, dict]:
        """
        A pre-flight method that performs fetch operations for a model year.  Useful for testing
        and as a 'pre-flight' to make sure that the manufacturer's API(s) haven't changed since
        the scraper was developed.
        :param date:
        :return: Dict consisting of Model Name (as str) and the fetched json data object
        """
        pass

    @abstractmethod
    def persistModelYear(self, date: 'date') -> None:
        pass

