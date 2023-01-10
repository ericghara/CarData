import logging
from unittest import TestCase

from transformer.transformers.toyota.LoggingTools import LoggingTools
from transformer.transformers.toyota.parser.BodyStyleParser import BodyStyleParser


class TestBodyStyleParser(TestCase):

    def setUp(self) -> None:
        self.loggingTools = LoggingTools(logging.getLogger() )
        self.bodyStyleParser = BodyStyleParser(self.loggingTools)

    def _parseModelAllAttributes(self):
        pass





