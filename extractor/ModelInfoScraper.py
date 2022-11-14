from typing import *
from abc import ABC, abstractmethod
from repository.Entities import Brand, RawData
from datetime import date
from repository.SessionFactory import sessionFactory

class ModelInfoScraper(ABC):

    def __init__(self, brand: 'Brand'):
        self.brand = brand

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

