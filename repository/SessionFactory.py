from sqlalchemy import create_engine
from glbls import variables
from sqlalchemy.engine import Engine

from sqlalchemy.orm import sessionmaker, Session


class SessionFactory:

    def __init__(self):
        self._URI_SCHEME = 'postgresql://'
        self._engine = None
        self._sessionGenerator = None

    def _createURI(self) -> str:
        if "@" in variables.POSTGRES_URI:  # assume it's a URI with username and password
            return variables.POSTGRES_URI
        if None in (variables.POSTGRES_USERNAME, variables.POSTGRES_PASSWORD, variables.POSTGRES_URI):
            raise AttributeError(
                f'Env variables {variables.POSTGRES_USERNAME}, {variables.POSTGRES_PASSWORD}, {variables.POSTGRES_URI} must be set!')
        if not variables.POSTGRES_URI.startswith(self._URI_SCHEME):
            raise ValueError(f'Connection uri must be prefixed with {self._URI_SCHEME}')
        # postgresql: // [user[:password] @][netloc]
        return f'{self._URI_SCHEME}{variables.POSTGRES_USERNAME}:{variables.POSTGRES_PASSWORD}@{variables.POSTGRES_URI[len(self._URI_SCHEME) - 1:]}'

    def getEngine(self) -> 'Engine':
        if not self._engine:
            self._engine = create_engine( self._createURI() )
        return self._engine

    def newSession(self) -> 'Session':
        if not self._sessionGenerator:
            self._sessionGenerator = sessionmaker(bind=self.getEngine() )
        return self._sessionGenerator()

    def purgeEngine(self) -> None:
        self._engine = None
        self._sessionGenerator = None

sessionFactory = SessionFactory()
