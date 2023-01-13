import logging
from unittest import TestCase

from nose_parameterized import parameterized

from transformer.common.attribute_dto import Grade
from transformer.transformers.toyota.LoggingTools import LoggingTools
from transformer.transformers.toyota.parser.GradeParser import GradeParser


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

    def test__parse(self):
        jsonData = {"model": [
            {"grade": {"attributes": {"title": {"value": "Grade"}}}},
            {"attributes": {"dealertrim": {"value": "Dealer Trim"}}},
            {}
        ]}
        foundGrades = self.gradeParser.parse(jsonData)
        expectedGrades = [Grade(title="Grade"), Grade(title="Dealer Trim"), Grade(title="Standard")]
        self.assertEqual(set(expectedGrades), set(foundGrades) )
