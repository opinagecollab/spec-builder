import csv
from os import path, getcwd

from spec_builder.crud.spec_repository import spec_repository
from spec_builder.model.question import Question


class QuestionsService:
    csv_file_path = './assets/fashion-specs-questions.csv'
    spec_column_name = 'SpecName'
    question_column_name = 'Question'

    def __init__(self, repository):
        self.spec_repository = repository

    def __parse_row(self, question_data, tenant_id):
        spec_name = question_data[self.spec_column_name].lower()
        spec = self.spec_repository.find_spec_by_name(spec_name, tenant_id)
        spec_id = spec.id
        question = question_data[self.question_column_name].format(header=spec_name)

        return Question(spec_id, spec_name, question)

    def retrieve_questions(self, tenant_id):
        base_dir = getcwd()
        file_path = path.abspath(path.join(base_dir, self.csv_file_path))
        questions = []
        with open(file_path, encoding='utf-8-sig') as csv_file:
            rows = csv.DictReader(csv_file)
            for row in rows:
                questions.append(self.__parse_row(row, tenant_id))

        return questions


questions_service = QuestionsService(spec_repository)
