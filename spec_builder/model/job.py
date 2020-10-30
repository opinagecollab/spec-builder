from enum import Enum


class JobStatus(Enum):
    NOT_STARTED = 0
    CREATE_TENANT_SPECS = 10
    INITIALIZE_CATEGORIES_DATA = 20
    ANALYZE_PRODUCTS = 30
    SUMMARIZE_CATEGORIES = 40
    CREATE_PRODUCT_INFERRED_SPECS = 50
    FINISHED = 60


class Job:

    def __init__(self, id, status):
        self.id = id
        self.status = status

    def __eq__(self, other):
        if not isinstance(other, Job):
            return NotImplemented

        return self.id == other.id

    def get_id(self):
        return self.id

    def get_status(self):
        return self.status

