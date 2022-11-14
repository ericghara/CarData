from unittest import TestCase

from repository.test_common.RepositorySetup import RepositorySetup


class TestModelService(TestCase):

    res = None

    @classmethod
    def setUpClass(cls):
        cls.res = RepositorySetup()
        cls.res.start()
        cls.res.initTables()
        cls.res.insetTestRecords()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.res.stop()

    def test__get_brand(self):
        self.fail()

    def test_get_model_year(self):
        self.fail()

    def test_get_model_by_brand_name_model_name_model_year(self):
        self.fail()

    def test_get_most_recent_model(self):
        self.fail()

    def test_get_models_by_brand_name_and_model_name(self):
        self.fail()

    def test_delete_model_by_brand_name_model_name_model_year(self):
        self.fail()

    def test_upsert(self):
        self.fail()
