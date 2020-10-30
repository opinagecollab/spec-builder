import pytest
from unittest.mock import ANY
from spec_builder.crud.job_repository import JobRepository
from spec_builder.model.job import Job


@pytest.fixture()
def db_connection(mocker):
    return mocker.patch('spec_builder.db.db_connection.DBConnection')


class TestJobRepository:

    def test_find_active_job_when_no_job_exists(self, db_connection):
        # ARRANGE - no job exists
        job_repository = JobRepository(db_connection)

        # ACT -
        result = job_repository.find_active_job()

        # ASSERT -
        db_connection.select.assert_called_once_with(ANY)
        assert result is None

    def test_find_active_job_when_job_exists(self, db_connection, mocker):
        # ARRANGE - Job exists
        some_id = 123
        some_status = 1
        job = (some_id, some_status)
        mocker.patch('spec_builder.db.db_connection.DBConnection.select', return_value=[job])
        job_repository = JobRepository(db_connection)

        # ACT -
        result = job_repository.find_active_job()

        # ASSERT -
        db_connection.select.assert_called_once_with(ANY)
        assert result == Job(some_id, some_status)

    def test_find_active_job_when_several_jobs_exist(self, db_connection, mocker):
        # Arrange - Multiple jobs exist
        expected_exception_str = "More than one job active. Another builder instance might be running or some cleanup is needed."

        job1 = mocker.Mock()
        job2 = mocker.Mock()

        mocker.patch('spec_builder.db.db_connection.DBConnection.select', return_value=[job1, job2])

        job_repository = JobRepository(db_connection)

        # ACT
        with pytest.raises(Exception) as exception_info:
            job_repository.find_active_job()

        # ASSERT
        db_connection.select.assert_called_once_with(ANY)
        assert expected_exception_str in str(exception_info.value)

    def test_create_job(self, db_connection, mocker):
        # ARRANGE
        expected_job_id = 789


        job_repository = JobRepository(db_connection)

        # ACT
        job_id = job_repository.create_job()

        # ASSERT
