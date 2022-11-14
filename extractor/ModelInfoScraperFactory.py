from sqlalchemy.engine.base import Engine

class ModelInfoScraperFactory:

    def __init__(self, connectionEngine: 'Engine' ):
        self.engine = connectionEngine

    #todo throw an error if Manufacturer or Brand cannot be fetched
    def generate(self, manufacturerCommon: str, brand: str) -> 'AbstractScraper':
        pass