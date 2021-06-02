from spec_builder.db.db_connection import db_connection
from spec_builder.crud.builder_repository import builder_repository
from spec_builder.model.job import Job, JobStatus


class JobRepository:

    def __init__(self, db):
        self.db = db
        self.builder_id = builder_repository.find_builder_id()
        self.__create_table()

    def __create_table(self):
        template = """
        
            CREATE TABLE IF NOT EXISTS lisa.spec_builder_job(
            
                id SERIAL PRIMARY KEY,
                builder_id CHARACTER VARYING NOT NULL,
                status INTEGER NOT NULL DEFAULT 0,
                
                FOREIGN KEY (builder_id) REFERENCES lisa.builder (id)
            
            );
        
        """

        self.db.insert(template, ())

    def find_active_job(self):
        query_template = f"""
            
            SELECT j.id, j.status FROM lisa.spec_builder_job AS j 
            WHERE 
                j.builder_id = '{ self.builder_id }' AND 
                j.status <> { JobStatus.FINISHED.value } 

        """

        active_jobs = self.db.select(query_template)
        if len(active_jobs) > 1:
            raise Exception("""
                More than one job active. Another builder instance might be running or some cleanup is needed.
            """)
        elif len(active_jobs) == 0:
            return None
        else:
            raw_job = active_jobs[0]
            return Job(raw_job[0], raw_job[1])

    def create_job(self):
        query_template = """
            
            INSERT INTO lisa.spec_builder_job(builder_id, status) VALUES(%s, %s)
            RETURNING id, status
            
        """

        status = JobStatus.NOT_STARTED.value
        raw_job = self.db.insert(query_template, (self.builder_id, status), True)
        return Job(raw_job[0], raw_job[1])

    def update_job_status(self, job_id, new_status):
        query_template = """
            
            UPDATE lisa.spec_builder_job
            SET status=%s 
            WHERE id=%s
            RETURNING id, status
            
        """

        raw_job = self.db.update(query_template, (new_status.value, job_id), True)
        return Job(raw_job[0], raw_job[1])


job_repository = JobRepository(db_connection)
