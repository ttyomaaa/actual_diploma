from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, HfArgumentParser
from pipelines import pipeline
from sentence_transformers import SentenceTransformer, util
from transformers import T5ForConditionalGeneration, T5Tokenizer
from itertools import groupby
import torch

KW_MODEL_PATH = 'C:/Users/User/PycharmProjects/diploma/model_working/keyt5-base'

QA_MODEL_PATH = 'C:/Users/User/PycharmProjects/diploma/model_working/t5-ru-new'
QG_MODEL_PATH = 'C:/Users/User/PycharmProjects/diploma/model_working/t5-ru'

QA_TOKENIZER_PATH = 'C:/Users/User/PycharmProjects/diploma/model_working/t5_ru_tokenizer-new'
QG_TOKENIZER_PATH = 'C:/Users/User/PycharmProjects/diploma/model_working/t5_ru_tokenizer'


def load_models():
    tokenizer_kw = T5Tokenizer.from_pretrained(KW_MODEL_PATH, local_files_only=True)
    model_kw = T5ForConditionalGeneration.from_pretrained(KW_MODEL_PATH, local_files_only=True)

    model_ss = SentenceTransformer('cointegrated/rubert-tiny2')

    tokenizer_qa = AutoTokenizer.from_pretrained(QA_TOKENIZER_PATH)
    model_qa = AutoModelForSeq2SeqLM.from_pretrained(QA_MODEL_PATH)

    tokenizer_qg = AutoTokenizer.from_pretrained(QG_TOKENIZER_PATH)
    model_qg = AutoModelForSeq2SeqLM.from_pretrained(QG_MODEL_PATH)

    qg = pipeline("e2e-qg", model=model_qg, tokenizer=tokenizer_qg)
    qa = pipeline("multitask-qa-qg", model=model_qa, tokenizer=tokenizer_qa)

    def generate(text, **kwargs):
        inputs = tokenizer_kw(text, return_tensors='pt')
        with torch.no_grad():
            hypotheses = model_kw.generate(**inputs, num_beams=5, **kwargs)
        s = tokenizer_kw.decode(hypotheses[0], skip_special_tokens=True)
        s = s.replace('; ', ';').replace(' ;', ';').lower().split(';')[:-1]
        s = [el for el, _ in groupby(s)]
        return s[0]

    def result_accuracy(answer, user_answer):
        embeddings = model_ss.encode([answer, user_answer])
        results = util.semantic_search(embeddings[0], embeddings[1:])[0]
        result_score = results[0]['score']
        return result_score

    return {"question": qg, "answer": qa, "keyword": generate, "result": result_accuracy}


