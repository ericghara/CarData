import logging
from unittest import TestCase

from common.domain.dto.AttributeDto import Package
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.transform.toyota.parser.LoggingTools import LoggingTools
from transformer.transform.toyota.parser.PackageParser import PackageParser


class TestPackageParser(TestCase):

    def setUp(self) -> None:
        loggingTools = LoggingTools(logging.getLogger())
        self.packageParser = PackageParser(loggingTools)

    def test__parseModelSinglePackageTitleAndPrice(self):
        model = {"packages": [
            {"title": "Technology Package",
             "price": "$770"}
        ]}
        foundPackages = list(self.packageParser._parseModel(model))
        expectedPackages = [Package(title="Technology Package",
                                    metadata=[AttributeMetadata(metadataType=MetadataType.COMMON_MSRP,
                                                                value=770, unit=MetadataUnit.DOLLARS)])
                            ]
        self.assertEqual(expectedPackages, foundPackages, "Regular equals")
        expectedPackages[0]._assertStrictEq(foundPackages[0])  # strict equality

    def test__parseModelSinglePackageTitleOnly(self):
        model = {"packages": [
            {"title": "Technology Package",
             "price": None}
        ]}
        foundPackages = list(self.packageParser._parseModel(model))
        expectedPackages = [Package(title="Technology Package")]
        self.assertEqual(expectedPackages, foundPackages, "Regular equals")
        expectedPackages[0]._assertStrictEq(foundPackages[0])  # strict equality

    def test__parseModelSinglePackageEmpty(self):
        model = {"packages": [
            {"title": None,
             "price": None}
        ]}
        foundPackageIter = self.packageParser._parseModel(model)
        self.assertRaises(StopIteration, lambda: next(foundPackageIter))

    def test__parseModelMultiplePackages(self):
        model = {"packages": [
            {"title": "Technology Package"},
            {"title": "50 State Emissions Package"},
            {"title": None},
            {}
        ]}
        foundPackages = set(self.packageParser._parseModel(model))
        expectedPackages = {Package("Technology Package"), Package("50 State Emissions Package")}
        self.assertEqual(expectedPackages, foundPackages)

    def test__parseHasDuplicatePackages(self):
        jsonData = {"model": [
            {"packages": [
                {"title": "Technology Package"}]},
            {"packages": [
                {"title": "Technology Package"}]}
        ]}
        foundPackages = self.packageParser.parse(jsonData)
        expectedPackages = [Package("Technology Package")]
        self.assertEqual(expectedPackages, foundPackages)

    def test_parseMultipleModels(self):
        jsonData = {"model": [
            {"packages": [
                {"title": "Technology Package"}]},
            {"packages": [
                {"title": "50 State Emissions Package"}]}
        ]}
        foundPackages = set(self.packageParser.parse(jsonData))
        expectedPackages = {Package("Technology Package"), Package("50 State Emissions Package")}
        self.assertEqual(expectedPackages, foundPackages)

    def test_parseModelKeepsHighestPriceOnDuplicate(self):
        jsonData = {"model": [
            {"packages": [
                {"title": "Technology Package",
                 "price": "$0.00"}]},
            {"packages": [
                {"title": "Technology Package",
                 "price": "$1,500.99"}]}
        ]}
        foundPackages = self.packageParser.parse(jsonData)
        expectedPackages = [Package(title="Technology Package",
                                   metadata=[AttributeMetadata(metadataType=MetadataType.COMMON_MSRP, value=1_501,
                                                               unit=MetadataUnit.DOLLARS)])]
        self.assertEqual(foundPackages, expectedPackages)
        expectedPackages[0]._assertStrictEq(foundPackages[0])
