from spec_builder.crud.job_product_repository import job_product_repository


class ProductSpecService:

    def __init__(self, job_product_repository):
        self.job_product_repository = job_product_repository

    def create_product_specs(self, job, tenant_id):
        products = self.job_product_repository.find_products_analyzed_in_job(job.id, tenant_id)
        for product in products:
            job_product_repository.create_product_inferred_specs(job.id, product.sku, product.tenant_id)


product_spec_service = ProductSpecService(job_product_repository)
