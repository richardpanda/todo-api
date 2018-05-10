import os

from dotenv import load_dotenv

load_dotenv()


class Config():
    DEBUG = True
    ENV = 'dev'
    JWT_SECRET = os.getenv('JWT_SECRET', 'secret')
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DB_URI', 'sqlite://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False


class TestingConfig(Config):
    DEBUG = False
    ENV = 'testing'
    SQLALCHEMY_DATABASE_URI = os.getenv('TESTING_DB_URI', 'sqlite://')
    TESTING = True
