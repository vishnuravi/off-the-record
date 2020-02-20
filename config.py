class Config(object):
    DEBUG = False
    TESTING = False

class DevelopmentConfig(Config):
    DEBUG = True
    SMS_NUMBER = '(415) 223-5601'
    SERVER_URL = 'https://offtherecord.vishnu.io'
    DOCTOR_NAME = 'Dr. Vishnu Ravi'