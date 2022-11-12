import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database

DATABASE_NAME = 'fyyurapp'
USERNAME = 'lieke'
PASSWORD = 'Glen2865'
HOST = 'localhost'
PORT = '5432'
# TODO IMPLEMENT DATABASE URL
#SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://lieke:Glen2865@localhost:5432/fyyurapp'
SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://{}:{}@{}:{}/{}".format(USERNAME, PASSWORD, HOST, PORT, DATABASE_NAME)