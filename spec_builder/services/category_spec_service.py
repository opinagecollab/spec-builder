import html
import logging

from spec_builder.crud.job_product_repository import job_product_repository
from spec_builder.crud.category_spec_repository import category_spec_repository
from spec_builder.crud.job_category_spec_repository import job_category_spec_repository
from spec_builder.services.questions_service import questions_service
from spec_builder.nlp.question_answering_classifier import QuestionAnsweringClassifier, QAModelType

log = logging.getLogger(__name__)


class CategorySpecService:

    def __init__(self):
        self.job_product_repository = job_product_repository
        self.qa_classifier = QuestionAnsweringClassifier(QAModelType.BERT_LARGE)
        self.questions_service = questions_service
        self.job_category_spec_repository = job_category_spec_repository
        self.category_spec_repository = category_spec_repository

    @staticmethod
    def __build_product_passage(product):
        product_passage = ''
        if product.name is not None:
            product_passage += product.name
        if product.description is not None:
            product_passage += product.description

        return html.unescape(product_passage)

    @staticmethod
    def __is_activated(answer):
        return answer != ''

    def initialize_categories_data(self, job, tenant_id):
        log.info(f'Initializing categories data for tenant {tenant_id}')
        self.job_category_spec_repository.create_all_category_spec_data(job.id, tenant_id)

    def __mark_product_as_processed(self, job, product):
        self.job_product_repository.mark_product_as_processed(job.id, product.sku, product.tenant_id)

    def __update_category_spec(self, job, category_id, spec_id, activated_for_product):
        self.job_category_spec_repository.upsert_category_spec_data(job.id, category_id, spec_id, activated_for_product)

    def analyze_products(self, job, tenant_id):
        products = self.job_product_repository.find_products_to_analyze(job.id, tenant_id)
        questions = self.questions_service.retrieve_questions(tenant_id)

        for product_count, product in enumerate(products, start=1):
            log.info(f'Analyzing product #{product_count} - Sku: {product.sku}')
            product_passage = self.__build_product_passage(product)

            log.debug(f'Product Passage {product_passage}')
            for question_template in questions:
                answer = self.qa_classifier.query(question_template.question, product_passage)
                log.debug(f'Question: {question_template.question}')
                log.debug(f'Answer: {answer}')
                activated_for_product = self.__is_activated(answer)

                for category_id in product.categories:
                    self.__update_category_spec(job, category_id, question_template.spec_id, activated_for_product)

            self.__mark_product_as_processed(job, product)

    def __summarize_category(self, job, tenant_id, category_spec_data, children_spec_data):
        # For now, the builder is only considering the specs directly activated for the category or for the
        # direct children - This means not considering grand-children or other descendants. This can be changed in
        # the future if needed.
        directly_activated = category_spec_data.directly_activated
        directly_not_activated = category_spec_data.directly_not_activated
        children_activated = children_spec_data.directly_activated if children_spec_data is not None else 0
        children_not_activated = children_spec_data.directly_not_activated if children_spec_data is not None else 0

        total_activated = directly_activated + children_activated
        total_not_activated = directly_not_activated + children_not_activated
        total = total_activated + total_not_activated

        percentage_activated = total_activated / total if total > 0 else 0

        self.job_category_spec_repository.update_activation_percentage(
            job.id, category_spec_data.category_id, category_spec_data.spec_id,
            children_activated, children_not_activated, percentage_activated
        )

        log.info(f"""
            - Updated: 
                Directly Activated: {directly_activated} Directly Not Activated: {directly_not_activated}
                Children Activated: {children_activated} Children Not Activated {children_not_activated}
                Percentage Activated: {percentage_activated}
        """)

    def summarize_categories(self, job, tenant_id):
        categories = self.job_category_spec_repository.find_categories_to_summarize(job.id, tenant_id)
        for category in categories:
            category_id = category.id
            log.info(f'Summarizing category {category_id}')

            category_spec_list = self.job_category_spec_repository.get_spec_data_by_category(job.id, category_id)
            for category_spec_data in category_spec_list:
                spec_id = category_spec_data.spec_id
                children_spec_data = \
                    self.job_category_spec_repository.get_children_spec_data_by_category(job.id, spec_id, category_id)

                self.__summarize_category(job, tenant_id, category_spec_data, children_spec_data)


category_spec_service = CategorySpecService()

