import logging
from abc import ABC, abstractmethod

from extractor.scraper.common.fetchModelData import ModelDtosAndJsonDataByName
from repository.Entities import Brand
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
        self.brand = self._queryBrandInfo(brand)
        self.log = logging.getLogger()


    # When noPersist=False, only required info in brand obj is Name, if brand_id is not null
    # the provided brand_id will be validated against the fetched brand
    # if noPersist=True, the provided Brand object is simply returned
    def _queryBrandInfo(self, brand: 'Brand') -> 'Brand':
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
    def _fetchModelYear(self, date: 'date' ) -> ModelDtosAndJsonDataByName:
        """
        Intended to be used by persist model year.  This should create all ``ModelDto``s and
        fetch their corresponding JSON model data.  Separation of this method from ``persistModelYear``
        is intended to allow a *dry-run* before actually running persist model year.
        :param date:
        :return: ``ModelDtosAndJsonDataByName`` tuple.  ``ModelDtos`` are simply a list of ModelDtos.
        ``JsonDataByName`` is a dictionary that allows the data for a ModelName to be quickly retrieved.
        This allows a way to associate JsonData with a ModelDto which is more flexible than keeping
        them as a tuple.
        """
        pass

    @abstractmethod
    def persistModelYear(self, date: 'date') -> None:
        pass

