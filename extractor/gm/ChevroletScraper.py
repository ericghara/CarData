import logging

from extractor.ModelInfoScraper import ModelInfoScraper


class ChevroletScraper(ModelInfoScraper):

    BRAND_NAME = 'chevrolet'
    DOMAIN = 'https://www.chevrolet.com'

    def __init__(self):
        pass

    def _getModelName(self, modelCode: str) -> str:
        if (foundModel := self.modelCodeToName.get(modelCode.lower() ) ):
            return foundModel
        else:
            modelName = modelCode.replace('-', " ").capitalize()
            # commercial vehicles most likely to fall through (i.e. Express van)
            if modelName.endswith('hd'): # for trucks and vans
                modelName = modelName[:-2] + modelName[-2:].upper()
            logging.info(f"Could not locate {modelCode}. Using model name {modelName}")
            return modelName