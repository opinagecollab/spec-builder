from spec_builder.db.db_connection import db_connection
from spec_builder.model.product import Product


class JobProductRepository:

    num_top_specs = 10

    def __init__(self, db):
        self.db = db
        self.__create_table()

    def __create_table(self):
        template = """
        
            CREATE TABLE IF NOT EXISTS lisa.spec_builder_job_product (
                
                job_id INTEGER NOT NULL,
                sku VARCHAR NOT NULL,
                tenant_id VARCHAR NOT NULL,
                
                PRIMARY KEY (job_id, sku, tenant_id),
                FOREIGN KEY (job_id) REFERENCES lisa.spec_builder_job (id),
                FOREIGN KEY (sku, tenant_id) REFERENCES lisa.product (sku, tenant_id)
            );
        
        """

        self.db.insert(template, ())

    @staticmethod
    def __parse_categories(categories_str):
        return categories_str.split(',')

    def find_products_to_analyze(self, job_id, tenant_id):
        query_template = f"""
            
            SELECT p.sku, p.tenant_id, p.name, p.description, string_agg(DISTINCT cp.category_id, ',') AS categories
            FROM lisa.product AS p, lisa.category_product AS cp
            WHERE 
            p.sku = cp.sku AND p.tenant_id = cp.tenant_id AND  
            p.tenant_id='{tenant_id}' AND p.sku NOT IN (
                SELECT j.sku FROM lisa.spec_builder_job_product  AS j WHERE j.job_id={job_id} AND j.tenant_id='{tenant_id}' 
            ) 
            GROUP BY p.sku, p.tenant_id, p.name, p.description 
        """

        rows = self.db.select_many(query_template)
        for row in rows:
            product_categories = self.__parse_categories(row[4])
            yield Product(row[0], row[1], row[2], row[3], product_categories)

    def find_products_analyzed_in_job(self, job_id, tenant_id):
        query_template = f"""
            
            SELECT p.sku, p.tenant_id, p.name, p.description 
            FROM lisa.spec_builder_job_product AS spec_prod, lisa.product AS p
            WHERE 
                spec_prod.job_id={job_id} AND spec_prod.tenant_id='{tenant_id}' AND 
                p.sku = spec_prod.sku AND p.tenant_id = spec_prod.tenant_id
            
        """

        rows = self.db.select_many(query_template)
        for row in rows:
            yield Product(row[0], row[1], row[2], row[3], None)

    def create_product_inferred_specs(self, job_id, sku, tenant_id):
        query_template = f"""
        
            WITH product_top_specs AS (
               SELECT p.tenant_id, p.sku, spec.spec_id, MAX(spec.percentage_activated) AS max_percentage
               FROM 
                  lisa.product AS p, 
                  lisa.category_product AS cp, 
                  lisa.spec_builder_job_category AS spec 
               WHERE 
                  p.sku='{sku}' AND p.tenant_id='{tenant_id}' AND
                  cp.sku=p.sku AND cp.tenant_id=p.tenant_id AND 
                  spec.job_id={job_id} AND spec.category_id=cp.category_id
               GROUP BY p.tenant_id, p.sku, spec.spec_id
               ORDER BY max_percentage DESC
               LIMIT {self.num_top_specs}
            )
            
            INSERT INTO lisa.product_spec (tenant_id, sku, spec_id, is_inferred)
               SELECT specs.tenant_id, specs.sku, specs.spec_id, TRUE
               FROM product_top_specs AS specs 
            ON CONFLICT DO NOTHING 
            
        """

        self.db.insert(query_template, ())

    def mark_product_as_processed(self, job_id, sku, tenant_id):
        query_template = """
        
            INSERT INTO lisa.spec_builder_job_product (job_id, sku, tenant_id)
            VALUES (%s, %s, %s)
            
        """

        self.db.insert(query_template, (job_id, sku, tenant_id))


job_product_repository = JobProductRepository(db_connection)
