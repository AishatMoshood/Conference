class Config(object):
    ADMIN_EMAIL = 'some params'
    USERNAME = 'Aishat Moshood'

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root@127.0.0.1/confdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    MERCHANT_ID = 't98765@0'


class TestConfig(Config):
    DATABASE_URI = 'Test Connection parameters'
