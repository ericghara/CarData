import logging
from abc import ABC, abstractmethod
from datetime import date
from extractor.scraper.common.fetchModelData import ModelDtosAndJsonDataByName

class ModelInfoScraper(ABC):

    def __init__(self, brandName: str, manufacturerCommon: str, **kwargs):
        super().__init__()
        self.brandName = brandName
        self.manufacturerCommon = manufacturerCommon
        self.log = logging.getLogger()

    def _validateModelYear(self, modelYear: date) -> None:
        if (modelYear.month != 1 or modelYear.day != 1):
            # override for manufacturers with multiple releases, ex. semi-annual
            raise ValueError(f'Month and day must be January 1st.')

    def getBrandName(self) -> str:
        return self.brandName

    def getManufacturerCommon(self) -> str:
        return self.manufacturerCommon

    @abstractmethod
    def fetchModelYear(self, date: 'date') -> ModelDtosAndJsonDataByName:
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
