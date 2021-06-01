import os
import logging

from spec_builder.model.job import JobStatus
from spec_builder.services.job_service import job_service
from spec_builder.services.tenant_service import tenant_service
from spec_builder.services.spec_service import spec_service
from spec_builder.services.category_spec_service import category_spec_service
from spec_builder.services.product_spec_service import product_spec_service
import builderfingerprint as bf
from builderfingerprint.enums import BuilderStatus

from spec_builder.nlp.question_answering_classifier import QAModelType, QuestionAnsweringClassifier

logging.basicConfig(level=os.environ.get("LOGLEVEL", "DEBUG"))
log = logging.getLogger(__name__)


def main(tenant_id):
    log.info('[Spec Builder] Running')
    # Set Builder status
    bf.set_builder_fingerprint_status(tenant_id,BuilderStatus.STARTED)

    job = job_service.get_active_job()

    # TODO: Do for all tenants - right now only for t2
    # tenant_ids = tenant_service.get_tenant_ids()
    
    log.info(f"Analyzing categories for tenant {tenant_id}")

    # Prepare data
    job_service.execute_job_step(JobStatus.CREATE_TENANT_SPECS,
                                    lambda: spec_service.create_specs_for_tenant(job, tenant_id))
    job_service.execute_job_step(JobStatus.INITIALIZE_CATEGORIES_DATA,
                                    lambda: category_spec_service.initialize_categories_data(job, tenant_id))

    # Start processing
    job_service.execute_job_step(JobStatus.ANALYZE_PRODUCTS,
                                    lambda: category_spec_service.analyze_products(job, tenant_id))
    job_service.execute_job_step(JobStatus.SUMMARIZE_CATEGORIES,
                                    lambda: category_spec_service.summarize_categories(job, tenant_id))

    # Create products specs
    job_service.execute_job_step(JobStatus.CREATE_PRODUCT_INFERRED_SPECS,
                                    lambda: product_spec_service.create_product_specs(job, tenant_id))

    # TODO: Clean-up database tables

    job_service.finalize_job()

    # Finalize job
    log.info('[Spec Builder] Finished')