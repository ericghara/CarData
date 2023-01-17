from unittest.mock import MagicMock

from sqlalchemy.orm import Session


class MockSessionFactory:

    def __init__(self):
        self.session = MagicMock()

    def newSession(self) -> 'Session':
        return self.session