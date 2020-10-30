import psycopg2
import logging

from spec_builder.config import (
    DATABASE_HOST,
    DATABASE_PORT,
    DATABASE_NAME,
    DATABASE_USERNAME,
    DATABASE_PASSWORD
)

log = logging.getLogger(__name__)


class DBConnection:

    def __init__(self, host, port, db_name, user, pwd):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.username = user
        self.password = pwd

        self.conn = None

    def connect(self):
        if self.conn is None:
            try:
                self.conn = psycopg2.connect(
                    host=self.host,
                    user=self.username,
                    password=self.password,
                    port=self.port,
                    dbname=self.db_name
                )
                log.debug('Connected to DB')
            except psycopg2.DatabaseError as e:
                log.error('Error connecting to database. ')
                raise e

    def insert(self, query, parameters, returns_value=False):
        return self.update(query, parameters, returns_value)

    def update(self, query, parameters, returns_value=False):
        self.connect()
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query, parameters)
                self.conn.commit()
                if returns_value:
                    result = cursor.fetchone()
                    return result
        except psycopg2.DatabaseError as e:
            log.error('Error writing to database')
            raise e

    def select_many(self, query, page_size=100):
        self.connect()
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                while True:
                    results = cursor.fetchmany(page_size)
                    if not results:
                        break
                    for result in results:
                        yield result
        except psycopg2.DatabaseError as e:
            log.error('Error reading from database')
            raise e

    def select(self, query):
        self.connect()
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except psycopg2.DatabaseError as e:
            log.error('Error reading from database')
            raise e


db_connection = DBConnection(
    DATABASE_HOST, DATABASE_PORT, DATABASE_NAME, DATABASE_USERNAME, DATABASE_PASSWORD
)
