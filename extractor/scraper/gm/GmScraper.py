from collections import namedtuple
from datetime import date
from typing import *

from extractor.scraper.ModelInfoScraper import ModelInfoScraper
from extractor.scraper.common.HttpClient import httpClient
from extractor.scraper.common.fetchModelData import ModelFetchDto, ModelDtosAndJsonDataByName

CarLineAndBodyStyle = namedtuple('CarLineAndBodyStyle', ['carLine', 'bodyStyle'] )
BodyStyleAndName = namedtuple('BodyStyleAndName', ['bodyStyle', 'name'] )


class GmScraper(ModelInfoScraper):
    MANUFACTURER_COMMON = "GM"
    BRAND_TO_DOMAIN = {'cadillac': 'https://www.cadillac.com',  # this isn't used
                       'buick': 'https://www.buick.com',
                       'chevrolet': 'https://www.chevrolet.com',
                       'gmc': 'https://www.gmc.com'}
    POSTAL_CODE = "94102" # postal code used for request params/headers, could affect availability/pricing

    # kwargs: noInit True/False, for testing doesn't fetch anything to initialize
    def __init__(self, brandName: str, domain: str, **kwargs):
        super().__init__(brandName=brandName, manufacturerCommon=self.MANUFACTURER_COMMON, **kwargs)
        self.domain = domain
        if not kwargs.get('noInit', False ):
            self.bodyStyleToName = self._getBodyStyleToName()
            self.bodyStyleToCarLine = self._getBodyStyleToCarLine()
        else:
            self.bodyStyleToName = dict()
            self.bodyStyleToCarLine = dict()

    def _generateModelListUrl(self) -> str:
        # ex: https://www.chevrolet.com/apps/atomic/shoppingLinks.brand=chevrolet.country=US.region=na.language=en.json
        return f'{self.domain}/apps/atomic/shoppingLinks.brand={self.brandName.lower() }.country=US.region=na.language=en.json'

    # data is optional: will fetch otherwise
    def _fetchCarLinesAndBodyStyles(self, year: int, data: Dict = None) -> List[CarLineAndBodyStyle]:
        if not data:
            url = self._generateModelListUrl()
            data = httpClient.getRequest(url).json()
        carLines = data.get(str(year))
        if carLines is None:
            raise ValueError(f'No models for year: {year} could be located.')
        found = list()
        for carLine, bodyStyles in carLines.items():
            for bodyStyle in bodyStyles:
                if bodyStyle:  # sometimes a base link is an empty string, discard
                    found.append(CarLineAndBodyStyle(bodyStyle=bodyStyle, carLine=carLine))
        return found

    # This api works for more recent model lists
    def _fetchBodyStylesAndNames(self, year: int) -> List[BodyStyleAndName]:
        # these are the minimum required headers, 415 or 400 responses if any less
        HEADERS = {'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8', 'clientApplicationId': 'quantum'}
        URL = self.domain + f'/bypass/pcf/vehicle-selector-service/v1/getVehicleInfo/{self.brandName.lower()}/us/b2c/en?requestType=models&year={year}'
        try:
            res = httpClient.getRequest(URL, headers=HEADERS)
        except RuntimeError:
            raise ValueError(f'Unable to fetch model year {year}.')
        modelYear = res.json().get('options')
        if not modelYear:
            raise ValueError(f'Unable to fetch model year {year}.')
        # in gm terminology bodystyle is a specific model in a carline (ie carline: corvette, bodystyle:
        # corvette-z06)
        stylesAndNames = list()
        for bodyStyle in modelYear:
            code = bodyStyle['code']
            name = bodyStyle['title']
            stylesAndNames.append(BodyStyleAndName(bodyStyle=code, name = name ) )
        return stylesAndNames

    def _getBodyStyleToName(self) -> dict:
        bodyStyleToName = dict()
        # notice iterating future to past
        # The getVehicleInfo api only returns current and previous model year, we look at last, current and next year
        # (expecting one to fail) to ensure that we catch those two years
        # Information may not be complete, i.e. Camaro missing from 2022 MY but present in 2023
        for year in range(date.today().year + 1, date.today().year - 2, -1):
            try:
                stylesAndNames = self._fetchBodyStylesAndNames(year)
            except ValueError:
                stylesAndNames = list()
                self.log.debug(f'Unable to fetch model year {year}. More than 1 failure could indicate a problem')
            for bodyStyle, name in stylesAndNames:
                bodyStyleToName.setdefault(bodyStyle, name)  # if duplicates keeps most recent
        return bodyStyleToName

    def _getBodyStyleToCarLine(self) -> Dict[str, str]:
        URL = self._generateModelListUrl()
        res = httpClient.getRequest(URL)
        shoppingLinks = res.json()
        minYear, maxYear = float('inf'), float('-inf')
        for year in shoppingLinks.keys():
            minYear = min(int(year), minYear)
            maxYear = max(int(year), maxYear)
        # if a duplicate name exists most recent year takes precedence
        bodyStyleToCarLine = dict()
        for year in range(maxYear, minYear - 1, -1):
            linesAndStyles = self._fetchCarLinesAndBodyStyles(year, shoppingLinks)
            for carLine, bodyStyle in linesAndStyles:
                bodyStyleToCarLine.setdefault(bodyStyle, carLine)
        return bodyStyleToCarLine

    # Returns bodyStyles found for model year from getVehicleInfo and shoppingLinks apis
    def _fetchBodyStyles(self, modelYear: 'date') -> Set[str]:
        # need to remove duplicates b/c we're aggregating results from 2 apis
        bodyStyles = set()
        try:
            # better for less recent model years, overall very complete for new model years as well
             carLinesAndBodyStyles = self._fetchCarLinesAndBodyStyles(modelYear.year)
        except ValueError:
            carLinesAndBodyStyles = list()
            self.log.debug(f'Unable to fetch year: {modelYear.year} from shoppingLinks API.')

        try:
            # only has data for past 2 model years
            bodyStylesAndNames = self._fetchBodyStylesAndNames(modelYear.year)
        except ValueError:
            bodyStylesAndNames = list()
            self.log.debug(f'Unable to fetch year: {modelYear.year} from getVehicleInfo API.')

        for _carLine, bodyStyle in carLinesAndBodyStyles:
            bodyStyles.add(bodyStyle)
        for bodyStyle, _name in bodyStylesAndNames:
            bodyStyles.add(bodyStyle)
        if not bodyStyles:
            raise ValueError(f'Unable to fetch data for model year: {modelYear}')
        return bodyStyles

    def _createModelDataPath(self,  carLine: str, bodyStyle: str, modelYear: date, **kwargs) -> str:
        """
        :param carLine:
        :param bodyStyle:
        :param modelYear:
        :param kwargs: ``api``: ``fullyConfigured`` - more information (includes all info from ``trim-matrix`` with a base configuration,
                                                    more likely to have server side error
                        ``api``: ``trim-matrix`` - default, less information, less likely to error
        :return: url to get json info
        """
        if kwargs.get('api', 'trim-matrix') == 'trim-matrix':
            return f'{self.domain}/byo-vc/api/v2/trim-matrix/en/US/{self.brandName.lower()}/{carLine}/{modelYear.year}/{bodyStyle}?postalCode={self.POSTAL_CODE}'
        elif kwargs['api'] == 'fullyConfigured':
            return f'{self.domain}/byo-vc/services/fullyConfigured/US/en/{self.brandName.lower()}/{modelYear.year}/{carLine}/{bodyStyle}?postalCode=94102&region=na'
        raise ValueError(f'Unrecognized api option {kwargs["api"]}')

    def _createModelFetchDto(self, bodyStyle: str, modelName: str, modelYear: date) -> ModelFetchDto:
        if None in (bodyStyle, modelName, modelYear):
            raise ValueError("Received a null argument.")
        try:
            carLine = self.bodyStyleToCarLine[bodyStyle]
        except KeyError as e:
            raise ValueError(f"Unable to match bodyStyle: {bodyStyle} with a carLine.", e)
        path = self._createModelDataPath(carLine=carLine, bodyStyle=bodyStyle, modelYear=modelYear)
        metadata = {"metadata" : { "bodyStyle": bodyStyle, "carLine" : carLine }}
        return ModelFetchDto(modelCode=bodyStyle, path=path, metadata=metadata, modelName=modelName)

    def fetchModelYear(self, date: 'date') -> ModelDtosAndJsonDataByName:
        """
        Extending classes should implement
        :param date:
        :return:
        """
        pass

    def _getModelName(self, bodySyle: str) -> str:
        """
        Extending classes should implement
        :param bodySyle:
        :return:
        """
        pass
