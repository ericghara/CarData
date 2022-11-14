import os
import logging
from sqlalchemy import create_engine
from typing import *

from sqlalchemy.orm import sessionmaker

# loger
logging.basicConfig(level=os.getenv('LOGGING_LEVEL') )

# sqlalchemy

USERNAME_KEY = 'POSTGRES_USERNAME'
PASSWORD_KEY = 'POSTGRES_PASSWORD'
URI_KEY = 'POSTGRES_URI'
URI_SCHEME = 'postgresql://'

def createURI() -> str:
    username = os.getenv(USERNAME_KEY)
    password = os.getenv(PASSWORD_KEY)
    uri = os.getenv(URI_KEY)
    if None in (username,password,uri ):
        raise AttributeError(f'Env variables {USERNAME_KEY}, {PASSWORD_KEY}, {URI_KEY} must be set!')
    if not uri.startswith(URI_SCHEME):
        raise ValueError(f'Connection uri must be prefixed with {URI_SCHEME}')
    # postgresql: // [user[:password] @][netloc]
    return f'{URI_SCHEME}{username}:{password}@{uri[len(URI_SCHEME)-1:]}'



engine = create_engine( createURI() )
Session = sessionmaker(bind=engine)