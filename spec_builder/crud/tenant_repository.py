from spec_builder.db.db_connection import db_connection


class TenantRepository:

    def __init__(self, db):
        self.db = db

    def get_all_tenant_ids(self):
        query_template = """
            
            SELECT id FROM lisa.tenant
        
        """

        rows = self.db.select(query_template)
        return map(lambda row: row[0], rows)


tenant_repository = TenantRepository(db_connection)

