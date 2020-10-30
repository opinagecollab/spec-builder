import logging
from spec_builder.crud.job_repository import job_repository
from spec_builder.model.job import JobStatus

log = logging.getLogger(__name__)

class JobService:

    def __init__(self, repository):
        self.job_repository = repository
        self.active_job = None

    def get_active_job(self):
        if self.active_job is None:
            self.active_job = self.job_repository.find_active_job()

        if self.active_job is None:
            self.active_job = self.job_repository.create_job()

        return self.active_job

    def execute_job_step(self, status, step_fn):
        job = self.get_active_job()

        if status.value < job.status:
            log.info(f'Skipping {status.name}. Already executed')
            return

        if job.status < status.value:
            self.active_job = self.job_repository.update_job_status(job.id, status)

        step_fn()

        log.info(f'Finished {status.name}')

    def finalize_job(self):
        job = self.get_active_job()
        self.job_repository.update_job_status(job.id, JobStatus.FINISHED)


job_service = JobService(job_repository)
