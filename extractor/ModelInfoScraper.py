from typing import *
from abc import ABC, abstractmethod
from repository import Brand, RawData
from datetime import date
from . import Session

class ModelInfoScraper(ABC):

    def __init__(self, brand: 'Brand'):
        self.brand = brand
        self.session = Session()

    def _validateModelYear(self, date: 'date') -> None:
        if (date.month != 1 or date.day != 1 ):
            # override for manufacturers with multiple releases, ex. semi-annual
            raise ValueError(f'Month and day must be January 1st.')

    @abstractmethod
    def _fetchModelYear(self, date: 'date' ) -> List['RawData']:
        pass

    @abstractmethod
    def persistModelYear(self, date: 'date') -> None:
        pass

