import pytest
from spec_builder.services.job_service import JobService
from spec_builder.model.job import Job, JobStatus


@pytest.fixture()
def job_repository(mocker):
    return mocker.patch('spec_builder.crud.job_repository.JobRepository')


class TestJobService:

    def test_initialize_job_when_no_previous_job_exists(self, job_repository, mocker):
        # ARRANGE - No previous job is returned
        expected_job_id = 123
        job_service = JobService(job_repository)
        mocker.patch('spec_builder.crud.job_repository.JobRepository.find_active_job', return_value=None)
        mocker.patch('spec_builder.crud.job_repository.JobRepository.create_job',
                     return_value=Job(expected_job_id, JobStatus.NOT_STARTED))
        mocker.patch('spec_builder.crud.job_repository.JobRepository.start_job',
                     return_value=Job(expected_job_id, JobStatus.IN_PROGRESS))

        # ACT
        job_returned = job_service.initialize_job()

        # ASSERT - New job is created and initialized
        job_repository.create_job.assert_called_once_with()
        job_repository.start_job.assert_called_once_with(expected_job_id)

        assert job_returned.id == expected_job_id
        assert job_returned.status == JobStatus.IN_PROGRESS

    def test_initialize_job_when_previous_job_not_started(self, job_repository, mocker):
        # ARRANGE
        expected_job_id = 456
        job_service = JobService(job_repository)
        mocker.patch('spec_builder.crud.job_repository.JobRepository.find_active_job',
                     return_value=Job(expected_job_id, JobStatus.NOT_STARTED))
        mocker.patch('spec_builder.crud.job_repository.JobRepository.start_job',
                     return_value=Job(expected_job_id, JobStatus.IN_PROGRESS))

        # ACT
        job_returned = job_service.initialize_job()

        # ASSERT - Previous job is updated and new job is not created
        job_repository.create_job.assert_not_called()
        job_repository.start_job.assert_called_once_with(expected_job_id)

        assert job_returned.id == expected_job_id
        assert job_returned.status == JobStatus.IN_PROGRESS

    def test_initialize_job_when_previous_job_in_progress(self, job_repository, mocker):
        # ARRANGE
        job_id = 123
        expected_exception_str = 'Another job is already in progress. Manual update is needed.'
        job_service = JobService(job_repository)

        mocker.patch('spec_builder.crud.job_repository.JobRepository.find_active_job',
                     return_value=Job(job_id, JobStatus.IN_PROGRESS))

        # ACT
        with pytest.raises(Exception) as exception_info:
            job_service.initialize_job()

        # ASSERT - Exception raised (manual action needed)
        assert expected_exception_str in str(exception_info.value)

    def test_initialize_job_when_multiple_jobs_exist(self):
        # ARRANGE - Multiple jobs exist - exception must be raised

        # ACT

        # ASSERT - Exception is raised

        pass