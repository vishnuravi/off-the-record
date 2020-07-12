class Config(object):
    DEBUG = False
    TESTING = False


class ProductionConfig(Config):
    SMS_NUMBER = '(123) 456-7890'
    SERVER_URL = 'https://offtherecord.vishnu.io'
    DOCTOR_NAME = 'Dr. Vishnu Ravi'
    MONGO_URI = 'mongodb://offtherecord_app:27017'


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = True
    SMS_NUMBER = '(123) 456-7890'
    SERVER_URL = 'http://localhost:5000'
    DOCTOR_NAME = 'Dr. Vishnu Ravi'
    MONGO_URI = 'mongodb://offtherecord_app:27017'
