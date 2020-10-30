from os import environ, path
from dotenv import load_dotenv

if 'DATABASE_HOST' not in environ:
    base_dir = path.abspath(path.dirname(__file__))
    file_path = path.abspath(path.join(base_dir, '../.env'))
    load_dotenv(file_path)

DATABASE_HOST = environ.get('DATABASE_HOST')
DATABASE_USERNAME = environ.get('DATABASE_USERNAME')
DATABASE_PASSWORD = environ.get('DATABASE_PASSWORD')
DATABASE_PORT = environ.get('DATABASE_PORT')
DATABASE_NAME = environ.get('DATABASE_NAME')
