import logging
from typing import Optional, Dict, List
from unittest import TestCase

from parameterized import parameterized

from common.domain.dto.AttributeDto import Package
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.transform.gm.parser.LoggingTools import LoggingTools
from transformer.transform.gm.parser.PackageParser import PackageParser


class TestPackageParser(TestCase):

    def setUp(self) -> None:
        loggingTools = LoggingTools(logging.getLogger(type(self).__name__))
        self.parser = PackageParser(loggingTools=loggingTools)

    @parameterized.expand([
        ({'description': "Technology Package", 'msrp': 2_000}, Package(title="Technology Package", metadata=[
            AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=2_000, unit=MetadataUnit.DOLLARS)]),
         "Title and price present"),
        ({'description': "Technology Package", 'msrp': None}, Package(title="Technology Package"),
         "Title present, price null"),
        ({'description': "Technology Package", 'msrp': "adfadfsa"}, Package(title="Technology Package"),
         "Title present, price incorrect format"),
        ({'description': "Technology Package"}, Package(title="Technology Package"),
         "Title present, no price key"),
        ({'description': None}, None, "Title null"),
        ({}, None, "Empty packageDict")
    ])
    def test__parsePackage(self, packageDict: Dict, expectedPackage: Optional[Package], testIdentifier: str):
        foundPackage = self.parser._parsePackage(packageDict=packageDict, modelIdentifier="test")
        self.assertEqual(expectedPackage, foundPackage, testIdentifier)
        if expectedPackage:
            expectedPackage._assertStrictEq(foundPackage)

    @parameterized.expand([
        ({"config": {"OPTIONS": {"PACKAGES": {"more": [{"description": "Technology Package"}]}}}},
         [Package(title="Technology Package")], "single package"),
        ({"config": {"OPTIONS": {"PACKAGES": {"more":
                                                  [{"description": "Technology Package"},
                                                   {"description": "ZL1 Package"}]}}}},
         [Package(title="Technology Package"), Package(title="ZL1 Package")], "two packages"),
        ({"config": {"OPTIONS": {"PACKAGES": {"more": None}}}}, [], "PACKAGES is null"),
        ({}, [], "Empty dataDict")
    ])
    def test_Parser(self, dataDict: Dict, expectedPackages: List[Package], testIdentifier: str):
        foundPackages = self.parser.parse(dataDict)
        self.assertEqual(expectedPackages, foundPackages, testIdentifier)
        packageByTitleFn = lambda packages: {package.title: package for package in packages}
        expectedPackagesByTitle = packageByTitleFn(expectedPackages)
        foundPackagesByTitle = packageByTitleFn(foundPackages)
        for title, expectedPackage in expectedPackagesByTitle.items():
            foundPackage = foundPackagesByTitle.get(title)
            expectedPackage._assertStrictEq(foundPackage)
