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

        answer_start_scores, answer_end_scores = self.model(input_ids, attention_mask)
        answer_start = torch.argmax(answer_start_scores)
        answer_end = torch.argmax(answer_end_scores) + 1

        raw_tokens = self.tokenizer.convert_ids_to_tokens(input_ids.tolist()[0][answer_start:answer_end])
        if len(raw_tokens) == 1 or (len(raw_tokens) >= 1 and raw_tokens[0] == self.tokenizer.cls_token):
            return ''

        # In some cases, the whole question is returned - return after the [SEP] token
        sep_token_index = next(
            (index for index, token in enumerate(raw_tokens) if token == self.tokenizer.sep_token), -1)
        raw_tokens = raw_tokens[:sep_token_index] if sep_token_index != -1 else raw_tokens

        return self.tokenizer.convert_tokens_to_string(raw_tokens)

