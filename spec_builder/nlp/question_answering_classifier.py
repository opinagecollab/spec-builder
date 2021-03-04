import logging
import torch

from enum import Enum
from transformers import AutoModelForQuestionAnswering, AutoTokenizer


class QAModelType(Enum):
    BERT_LARGE = 1
    ROBERTA_BASE = 2


QA_MODELS = {
    QAModelType.BERT_LARGE: "deepset/bert-large-uncased-whole-word-masking-squad2",
    QAModelType.ROBERTA_BASE: "deepset/roberta-base-squad2"
}

log = logging.getLogger(__name__)


class QuestionAnsweringClassifier:

    max_length = 512

    def __init__(self, model_type):

        if torch.cuda.is_available():
            self.device = torch.device('cuda')
            log.info("Running analysis in GPU")
        else:
            self.device = torch.device('cpu')
            log.info("No GPU found. Analysis will be done in CPU.")

        model_name = QA_MODELS.get(model_type)
        log.info(f"Selected {model_name} for QA analysis.")

        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForQuestionAnswering.from_pretrained(model_name).to(self.device)

    def query(self, question, passage):
        encoding = self.tokenizer.encode_plus(
            question,
            passage,
            max_length=self.max_length,
            # pad_to_max_length=True,
            padding='max_length',
            truncation=True,
            add_special_tokens=True,
            return_tensors="pt"
        )

        input_ids = encoding['input_ids'].to(self.device)
        attention_mask = encoding['attention_mask'].to(self.device)

        passage_start_pos = input_ids.tolist()[0].index(self.tokenizer.sep_token_id) + 1
        passage_end_pos = self.max_length - 1
        if 0 in attention_mask.tolist()[0]:
            passage_end_pos = attention_mask.tolist()[0].index(0) - 1

        answer_start_scores, answer_end_scores = self.model(input_ids, attention_mask)
        answer_start = torch.argmax(answer_start_scores)
        answer_end = torch.argmax(answer_end_scores) + 1

        if answer_start < passage_start_pos:
            answer_start = passage_start_pos

        if answer_end < passage_start_pos:
            answer_end = passage_start_pos
        elif answer_end > passage_end_pos:
            answer_end = passage_end_pos

        raw_tokens = self.tokenizer.convert_ids_to_tokens(input_ids.tolist()[0][answer_start:answer_end])
        if len(raw_tokens) == 0 or (len(raw_tokens) == 1 and self.tokenizer.cls_token):
            return ''

        return self.tokenizer.convert_tokens_to_string(raw_tokens)

