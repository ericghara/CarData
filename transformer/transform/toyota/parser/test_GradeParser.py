import logging
from unittest import TestCase

from parameterized import parameterized

from common.domain.dto.AttributeDto import Grade
from common.domain.dto.AttributeMetadata import AttributeMetadata
from common.domain.enum.MetadataType import MetadataType
from common.domain.enum.MetadataUnit import MetadataUnit
from transformer.transform.toyota.parser.LoggingTools import LoggingTools
from transformer.transform.toyota.parser.GradeParser import GradeParser


class TestGradeParser(TestCase):

    def setUp(self):
        loggingTools = LoggingTools(logging.getLogger())
        self.gradeParser = GradeParser(loggingTools)

    @parameterized.expand([("Grade", None, "Grade"),
                           (None, "Dealer Trim", "Dealer Trim"),
                           (None, None, "Standard"),
                           ('Grade', 'Dealer Trim', 'Grade')  # <=shouldn't happen, but want to define behavior
                           ])
    def test__parseModelNullDealerTrimAndNullGrade(self, grade, dealerTrim, expectedTitle):
        modelWithNulls = {"grade": {"attributes": {"title": {"value": grade}}},
                          "attributes": {"dealertrim": {"value": dealerTrim}}
                          }
        foundGrade = self.gradeParser._parseModel(modelWithNulls)
        expectedGrade = Grade(title=expectedTitle)
        expectedGrade._assertStrictEq(foundGrade)

    def test_parseModelWithPrice(self):
        model = {"attributes": {"msrp": {"value": "$100"}}}
        foundGrade = self.gradeParser._parseModel(model)
        expectedGrade = Grade(title="Standard",
                              metadata=[AttributeMetadata(metadataType=MetadataType.COMMON_BASE_MSRP,
                                                          value=100, unit=MetadataUnit.DOLLARS)])
        expectedGrade._assertStrictEq(foundGrade)

    def test__parse(self):
        jsonData = {"model": [
            {"grade": {"attributes": {"title": {"value": "Grade"}}}},
            {"attributes": {"dealertrim": {"value": "Dealer Trim"}}},
            {}
        ]}
        foundGrades = self.gradeParser.parse(jsonData)
        expectedGrades = [Grade(title="Grade"), Grade(title="Dealer Trim"), Grade(title="Standard")]
        self.assertEqual(set(expectedGrades), set(foundGrades))

    def test__parseLowestPriceOnConflict(self):
        jsonData = {"model": [
            {"grade": {"attributes": {"title": {"value": "Grade"}}},
             "attributes" : {"msrp" : {"value" : "$30,000"}}},
            {"grade": {"attributes": {"title": {"value": "Grade"}}},
             "attributes": {"msrp": {"value": "$29,999"}}}
        ]}
        foundGrades = self.gradeParser.parse(jsonData)
        expectedGrades = [Grade(title="Grade", metadata=[AttributeMetadata(metadataType=MetadataType.COMMON_BASE_MSRP,
                                                          value=29_999, unit=MetadataUnit.DOLLARS)])]
        self.assertEqual(expectedGrades, foundGrades)
        expectedGrades[0]._assertStrictEq(foundGrades[0])
