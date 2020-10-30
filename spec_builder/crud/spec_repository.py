from spec_builder.model.spec import Spec
from spec_builder.db.db_connection import db_connection


class SpecRepository:

    def __init__(self, db):
        self.db = db
        pass

    def insert_spec(self, spec_id, name):
        query_template = """
            
            INSERT INTO lisa.spec(id, name, base_unit_name, base_unit_symbol, comparable) VALUES(%s, %s, '.', '.', TRUE)
            ON CONFLICT DO NOTHING
        
        """

        self.db.insert(query_template, (spec_id, name))

    def find_spec_by_name(self, spec_name, tenant_id):
        query_template = f"""
            
            SELECT id, name FROM lisa.spec
            WHERE id LIKE '{tenant_id}-%' AND name='{spec_name}'
            
        """

        result = self.db.select(query_template)

        if len(result) == 0:
            raise Exception(f'Cannot find spec with name {spec_name} for tenant {tenant_id}')

        raw_data = result[0]

        return Spec(raw_data[0], raw_data[1])


spec_repository = SpecRepository(db_connection)

