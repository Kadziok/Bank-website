import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://test:haslo123@localhost/desp'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
