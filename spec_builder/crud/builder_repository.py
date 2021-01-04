from spec_builder.db.db_connection import db_connection

BUILDER_NAME = 'spec-builder'


class BuilderRepository:

    def __init__(self, db):
        self.db = db
        self.__create_table()

    def __create_table(self):
        template = """
        
            CREATE TABLE IF NOT EXISTS lisa.builder (
                id SERIAL NOT NULL, 
                name VARCHAR NOT NULL UNIQUE, 
                
                PRIMARY KEY (id)
            )
        
        """

        self.db.insert(template, ())

    def __register_builder(self):
        template = """
            
            INSERT INTO lisa.builder(name) VALUES (%s)
            RETURNING id
        
        """

        return self.db.insert(template, (BUILDER_NAME,), True)

    def find_builder_id(self):
        query_template = f"""
            
            SELECT id FROM lisa.builder
            WHERE name='{BUILDER_NAME}'
        
        """

        builders = self.db.select(query_template)

        if len(builders) == 0:
            builders = self.__register_builder()
            return builders[0]
        else:
            builder = builders[0]
            return builder[0]


builder_repository = BuilderRepository(db_connection)
