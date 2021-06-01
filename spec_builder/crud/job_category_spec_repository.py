from spec_builder.model.category import Category
from spec_builder.model.category_spec_data import CategorySpecData
from spec_builder.db.db_connection import db_connection


class JobCategorySpecRepository:

    def __init__(self, db):
        self.db = db
        self.__create_table()

    def __create_table(self):
        template = """
            
            CREATE TABLE IF NOT EXISTS lisa.spec_builder_job_category (

                job_id INTEGER NOT NULL,
                category_id VARCHAR NOT NULL, 
                spec_id VARCHAR NOT NULL, 
                directly_activated INTEGER NOT NULL DEFAULT 0,
                directly_not_activated INTEGER NOT NULL DEFAULT 0, 
                children_activated INTEGER NOT NULL DEFAULT 0, 
                children_not_activated INTEGER NOT NULL DEFAULT 0,
                percentage_activated NUMERIC (5, 2),
                
                PRIMARY KEY (job_id, category_id, spec_id),
                FOREIGN KEY (job_id) REFERENCES lisa.spec_builder_job (id),
                FOREIGN KEY (category_id) REFERENCES lisa.category (id),
                FOREIGN KEY (spec_id) REFERENCES lisa.spec (id)
            );    
            
        """

        self.db.insert(template, ())

    def create_all_category_spec_data(self, job_id, template_id):
        template = f"""
        
            INSERT INTO lisa.spec_builder_job_category (job_id, category_id, spec_id)
            SELECT {job_id}, cat.id, s.id FROM lisa.category AS cat
            CROSS JOIN lisa.spec s
            WHERE cat.id LIKE '{template_id}%%' AND s.id LIKE '{template_id}-%%'
            ON CONFLICT DO NOTHING
        
        """

        self.db.update(template, ())

    def upsert_category_spec_data(self, job_id, category_id, spec_id, is_activated):
        num_activated = 1 if is_activated else 0
        num_not_activated = 0 if is_activated else 1

        template = f"""
        
            INSERT INTO 
                lisa.spec_builder_job_category(job_id, category_id, spec_id, directly_activated, directly_not_activated)
                VALUES ({job_id}, '{category_id}', '{spec_id}', {num_activated}, {num_not_activated})
            ON CONFLICT (job_id, category_id, spec_id) DO UPDATE 
                SET directly_activated = lisa.spec_builder_job_category.directly_activated + {num_activated}, 
                    directly_not_activated = lisa.spec_builder_job_category.directly_not_activated + {num_not_activated}
            
        """

        self.db.update(template, ())

    def update_activation_percentage(self, job_id, category_id, spec_id, children_activated, children_not_activated,
                                     percentage_activated):
        template = f"""

            UPDATE lisa.spec_builder_job_category
                SET 
                    children_activated={children_activated}, 
                    children_not_activated={children_not_activated}, 
                    percentage_activated={percentage_activated}
                WHERE job_id={job_id} AND category_id='{category_id}' AND spec_id='{spec_id}'
            
        """

        self.db.update(template, ())

    def __find_categories_ready_to_summarize(self, job_id, tenant_id):

        template = f"""

            WITH categories_status AS (
                    SELECT 
                        cat_spec.category_id, 
                    SUM( 
                        CASE WHEN cat_spec.percentage_activated IS DISTINCT FROM NULL THEN 1 ELSE 0 END 
                    ) AS specs_processed,
                    COUNT(cat_spec.category_id) AS total_specs
                FROM lisa.spec_builder_job_category AS cat_spec
                WHERE cat_spec.job_id={job_id}
                GROUP BY cat_spec.category_id
            )
            
            SELECT cat.id, cat.name
            FROM 
                lisa.category AS cat, categories_status AS status
            WHERE 
                cat.id LIKE '{tenant_id}%' AND 
                
                -- Category hasn't been processed
                cat.id = status.category_id AND status.specs_processed <> status.total_specs AND 
            
                -- Category shouldn't have any children that hasn't been processed 
                cat.id NOT IN (
                    SELECT cat.id
                    FROM lisa.category AS cat, lisa.category_parent AS cat_to_cat, categories_status AS status
                    WHERE 
                                cat.id = cat_to_cat.parent_id AND 
                                cat_to_cat.category_id = status.category_id AND 
                                status.specs_processed <> status.total_specs
                )

        """

        return self.db.select(template)

    def find_categories_to_summarize(self, job_id, tenant_id):
        while True:
            categories = self.__find_categories_ready_to_summarize(job_id, tenant_id)
            if len(categories) == 0:
                break

            for raw_category in categories:
                yield Category(raw_category[0], raw_category[1])

    def get_spec_data_by_category(self, job_id, category_id):
        template = f"""	
            SELECT 
                category_id, spec_id, directly_activated, directly_not_activated, 
                children_activated, children_not_activated
            FROM 
                lisa.spec_builder_job_category
            WHERE 
                job_id={job_id} AND category_id='{category_id}'
        """

        rows = self.db.select(template)

        for row in rows:
            yield CategorySpecData(
                category_id=row[0],
                spec_id=row[1],
                directly_activated=row[2],
                directly_not_activated=row[3],
                children_activated=row[4],
                children_not_activated=row[5]
            )

    def get_children_spec_data_by_category(self, job_id, spec_id, category_id):
        template = f"""
            
            SELECT 
               cat_spec.spec_id, 
               SUM(cat_spec.directly_activated) AS directly_activated, 
               SUM(directly_not_activated) AS directly_not_activated, 
               SUM(children_activated) AS children_activated,
               SUM(children_not_activated) AS children_not_activated
            FROM 
               lisa.spec_builder_job_category AS cat_spec 
            WHERE 
               cat_spec.job_id = {job_id} AND 
               cat_spec.spec_id = '{spec_id}' AND
               cat_spec.category_id IN 
               (
                   SELECT DISTINCT
                      cat_to_cat.category_id
                   FROM
                      lisa.category_parent AS cat_to_cat 
                   WHERE
                      cat_to_cat.parent_id = '{category_id}'
               )
            GROUP BY cat_spec.spec_id
            
        """

        rows = self.db.select(template)
        if len(rows) == 0:
            return None

        raw_data = rows[0]

        return CategorySpecData(
            parent_category_id=category_id,
            spec_id=raw_data[0],
            directly_activated=raw_data[1],
            directly_not_activated=raw_data[2],
            children_activated=raw_data[3],
            children_not_activated=raw_data[4]
        )


job_category_spec_repository = JobCategorySpecRepository(db_connection)
