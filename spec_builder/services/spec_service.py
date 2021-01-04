import csv
import logging
from os import path, getcwd

from spec_builder.crud.spec_repository import spec_repository

log = logging.getLogger(__name__)


# Notes:
# - Currently, all the specs (and questions) are the same for all "domains".
#
class SpecService:

    csv_file_path = './assets/fashion-specs.csv'

    def __init__(self, repository):
        self.spec_repository = repository
        pass

    def __read_specs_from_csv(self):
        base_dir = getcwd()
        file_path = path.abspath(path.join(base_dir, self.csv_file_path))
        spec_names = []
        with open(file_path, encoding='utf-8-sig') as csv_file:
            rows = csv.DictReader(csv_file)
            for row in rows:
                spec_names.append(row['name'])

        return spec_names

    @staticmethod
    def __build_spec_id(tenant_id, index):
        return f"{tenant_id}-{index}"

    def create_specs_for_tenant(self, job, tenant_id):
        log.info(f'Creating specs for tenant - {tenant_id}')
        spec_names = self.__read_specs_from_csv()

        for index, spec_name in enumerate(spec_names, start=1):
            spec_id = self.__build_spec_id(tenant_id, index)
            spec_repository.insert_spec(spec_id, spec_name)

        pass


spec_service = SpecService(spec_repository)

