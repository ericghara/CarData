import logging
from unittest import TestCase

from transformer.common.attribute_dto import Package
from transformer.common.dto import AttributeMetadata
from transformer.common.enum.MetadataType import MetadataType
from transformer.common.enum.MetadataUnit import MetadataUnit
from transformer.transformers.toyota.LoggingTools import LoggingTools
from transformer.transformers.toyota.parser.PackageParser import PackageParser


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

    def test__parseModelHasDuplicatePackages(self):
        modelJson = {"model": [
            {"packages": [
                {"title": "Technology Package"}]},
            {"packages": [
                {"title": "Technology Package"}]}
        ]}
        foundPackages = self.packageParser.parse(modelJson)
        expectedPackages = [Package("Technology Package")]
        self.assertEqual(expectedPackages, foundPackages)

    def test_parseModelMultipleModels(self):
        modelJson = {"model": [
            {"packages": [
                {"title": "Technology Package"}]},
            {"packages": [
                {"title": "50 State Emissions Package"}]}
        ]}
        foundPackages = set(self.packageParser.parse(modelJson))
        expectedPackages = {Package("Technology Package"), Package("50 State Emissions Package")}
        self.assertEqual(expectedPackages, foundPackages)
