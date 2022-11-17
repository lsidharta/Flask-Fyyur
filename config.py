import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))
# Enable debug mode.
DEBUG = True
SQLALCHEMY_ECHO = True
SQLALCHEMY_TRACK_MODIFICATIONS = False
# Connect to the database
DATABASE_NAME = 'fyyurapp'
USERNAME = 'lieke'
PASSWORD = 'Glen2865'
HOST = 'localhost'
PORT = '5432'
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(USERNAME, PASSWORD, HOST, PORT, DATABASE_NAME)