from os import environ, path
from dotenv import load_dotenv

if 'DATABASE_HOST' not in environ:
    base_dir = path.abspath(path.dirname(__file__))
    file_path = path.abspath(path.join(base_dir, '../.env'))
    load_dotenv(file_path)

DATABASE_HOST = environ.get('DATABASE_HOST') or 'localhost'
DATABASE_USERNAME = environ.get('DATABASE_USERNAME') or 'warehouse'
DATABASE_PASSWORD = environ.get('DATABASE_PASSWORD') or 'warehouse'
DATABASE_PORT = environ.get('DATABASE_PORT') or '5432'
DATABASE_NAME = environ.get('DATABASE_NAME') or 'warehouse'
