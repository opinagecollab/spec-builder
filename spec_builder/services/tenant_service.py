import logging
from spec_builder.crud.tenant_repository import tenant_repository

log = logging.getLogger(__name__)


class TenantService:

    def __init__(self, repository):
        self.tenant_repository = repository

    def get_tenant_ids(self):
        logging.debug('Retrieving tenants')
        return self.tenant_repository.get_all_tenant_ids()


tenant_service = TenantService(tenant_repository)
