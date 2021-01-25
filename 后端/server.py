import argparse
import glob
import json
import logging
import math
import os
import random
import re
import sys

import jieba
from flask_cors import CORS
import numpy as np
import torch
from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
from torch.utils.data import (DataLoader, RandomSampler, SequentialSampler,
                              TensorDataset)
from torch.utils.data.distributed import DistributedSampler
from tqdm import tqdm, trange

from creeper import creeper_v1, creeper_v2
from mrc import mrc_MODEL_CLASSES, mrc_predict, set_seed, to_list
from rerank import rerank_MODEL_CLASSES, rerank_predict

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


class Args(object):
    def __init__(self, config: dict):
        for key, value in config.items():
            self.__dict__[key] = value


class Mrc(object):
    """
    ADD KEYS:
    answer: string
    mrc_logits: float 
    """    
    def __init__(self, config: dict):
        """
        Loading args, model, tokenizer
        """
        logger.info("***** Mrc model initing *****")
        args = Args(config['mrc'])

        # Setup CUDA, GPU & distributed training
        if args.local_rank == -1 or args.no_cuda:
            device = torch.device("cuda" if torch.cuda.is_available() and not args.no_cuda else "cpu")
            args.n_gpu = torch.cuda.device_count()
        else:  # Initializes the distributed backend which will take care of sychronizing nodes/GPUs
            torch.cuda.set_device(args.local_rank)
            device = torch.device("cuda", args.local_rank)
            torch.distributed.init_process_group(backend='nccl')
            args.n_gpu = 1    
        args.device = device
       
        # Set seed
        set_seed(args)

        # Load pretrained model and tokenizer
        if args.local_rank not in [-1, 0]:
            torch.distributed.barrier()  # Make sure only the first process in distributed training will download model & vocab

        # model_name_or_path: the path of pre-trained_model or checkpoint
        args.model_type = args.model_type.lower()
        config_class, model_class, tokenizer_class = mrc_MODEL_CLASSES[args.model_type]
        self.config = config_class.from_pretrained(args.model_name_or_path)
        self.tokenizer = tokenizer_class.from_pretrained(args.model_name_or_path, do_lower_case=args.do_lower_case)
        self.model = model_class.from_pretrained(args.model_name_or_path, from_tf=bool('.ckpt' in args.model_name_or_path), config=self.config)

        if args.local_rank == 0:
            torch.distributed.barrier()  # Make sure only the first process in distributed training will download model & vocab

        self.model.to(args.device)
        self.args = args

        logger.info("Training/evaluation parameters %s", args)

        
    def predict(self, examples):
        """
        all_predictions:
        {
            'question_id': answer string,
            'question_id': answer string,
            ...
            ...
        }
        all_nbest_json:
        {
            'question_id':[
                {
                    "text": string,
                    "probability": float,
                    "start_logit": float,
                    "end_logit": float
                },
                {
                    "text": string,
                    "probability": float,
                    "start_logit": float,
                    "end_logit": float
                },
                ...(top 20)
            ]
        }

        examples:
        [
            {
                'question_id': int,
                'question': string,
                'title': string,
                'abstract': string,
                'source_link': url,
                'content': string,
                'doc_tokens': string,
            },
            {
            ...
            }
        ]       
        """
        all_predictions, all_nbest_json = mrc_predict(self.args, self.model, self.tokenizer, examples)
        assert len(all_predictions) == len(examples)
        assert len(all_nbest_json) == len(examples)
        for example in examples:
            qid = example['question_id']
            logitslist =[var['start_logit'] + var['end_logit'] for var in all_nbest_json[qid]]
            problist = [var['start_prob'] * var['end_prob'] for var in all_nbest_json[qid]]
            problist_v1 = [var['start_prob_v1'] * var['end_prob_v1'] for var in all_nbest_json[qid]]
            example['answer'] = all_predictions[qid].replace('\n', '').replace(' ', '').strip()
            example['mrc_logits'] = sum(logitslist)/len(logitslist)
            example['mrc_prob'] = sum(problist)/len(problist)
            example['mrc_prob_v1'] = sum(problist_v1)/len(problist_v1)
        return examples


class Rerank(object):
    """
    ADD KEY:
    rerank_logits: float
    """
    def __init__(self, config: dict):
        """
        Loading args, model, tokenizer
        """
        logger.info("***** Rerank model initing *****")
        args = Args(config['rerank'])

        # Setup CUDA, GPU & distributed training
        if args.local_rank == -1 or args.no_cuda:
            device = torch.device("cuda" if torch.cuda.is_available() and not args.no_cuda else "cpu")
            args.n_gpu = torch.cuda.device_count()
        else:  # Initializes the distributed backend which will take care of sychronizing nodes/GPUs
            torch.cuda.set_device(args.local_rank)
            device = torch.device("cuda", args.local_rank)
            torch.distributed.init_process_group(backend='nccl')
            args.n_gpu = 1    
        args.device = device
       
        # Set seed
        set_seed(args)

        # Load pretrained model and tokenizer
        if args.local_rank not in [-1, 0]:
            torch.distributed.barrier()  # Make sure only the first process in distributed training will download model & vocab

        # model_name_or_path: the path of pre-trained_model or checkpoint
        args.model_type = args.model_type.lower()
        config_class, model_class, tokenizer_class = rerank_MODEL_CLASSES[args.model_type]
        self.config = config_class.from_pretrained(args.model_name_or_path)
        self.tokenizer = tokenizer_class.from_pretrained(args.model_name_or_path, do_lower_case=args.do_lower_case)
        self.model = model_class.from_pretrained(args.model_name_or_path, from_tf=bool('.ckpt' in args.model_name_or_path), config=self.config)

        if args.local_rank == 0:
            torch.distributed.barrier()  # Make sure only the first process in distributed training will download model & vocab

        self.model.to(args.device)
        self.args = args

        logger.info("Training/evaluation parameters %s", args)


    def predict(self, examples):
        all_rerank_logits = rerank_predict(self.args, self.model, self.tokenizer, examples)
        assert len(all_rerank_logits) == len(examples)
        for example in examples:
            qid = example['question_id']
            example['rerank_logits'] = all_rerank_logits[qid][1]
        return examples


class Choose(object):
    """
    ADD key:
    rank_index
    final_prob
    pp_pm_pr: list, for debug
    """
    def __init__(self):
        self.pre_prob = [0.503, 0.3314, 0.1414, 0.0831, 0.0411]

    def clean_answer(self, text):
        dr = re.compile(r'<[^>]+>', re.S)
        dd = dr.sub('', text)
        newtext = dd.replace('\n', '').lstrip('。').lstrip('，')
        return newtext   

    def _compute_softmax(self, scores):
        """Compute softmax probability over raw logits."""
        if not scores:
            return []

        max_score = None
        for score in scores:
            if max_score is None or score > max_score:
                max_score = score

        exp_scores = []
        total_sum = 0.0
        for score in scores:
            x = math.exp(score - max_score)
            exp_scores.append(x)
            total_sum += x

        probs = []
        for score in exp_scores:
            probs.append(score / total_sum)
        return probs

    def process(self, examples):
        mrc_prob = []
        rerank_prob = []
        for example in examples:
            mrc_prob.append(example['mrc_logits'])
            rerank_prob.append(example['rerank_logits'])
        mrc_prob = self._compute_softmax(mrc_prob)
        rerank_prob = self._compute_softmax(rerank_prob)
        for example, pp, pm, pr in zip(examples, self.pre_prob, mrc_prob, rerank_prob):
            example['final_prob'] = pp * pm * pr
            example['pp_pm_pr'] = [pp, pm, pr]
            example['answer'] = self.clean_answer(example['answer'])
        examples = sorted(examples, key=lambda x: x['final_prob'], reverse=True)
        return examples
    

class Demo(object):
    def __init__(self, config_path):
        self.server_config = json.loads(open(config_path).read())
        self.mrc_processor = Mrc(self.server_config)
        self.rerank_processor = Rerank(self.server_config)
        self.choose_processor = Choose()
        if self.server_config["creeper"]["creeper_type"] == 'v1':
            self.creeper = creeper_v1
        else:
            self.creeper = creeper_v2
        self.keys = [
            "question_id",
            "question",
            "title",
            "abstract",
            "source_link",
            "content",
            "answer",
            "final_prob",
            "final_prob_v1"
        ]

    def filter(self, examples, keys):
        new_examples = []
        for example in examples:
            new_example = {}
            for key in example:
                if key in keys:
                    new_example[key] = example[key]
            new_examples.append(new_example)
        return new_examples

    def predict(self, query):
        # 读取一个问题的5篇文档
        examples = self.creeper(query)
        # 预测5个文档的答案
        examples = self.mrc_processor.predict(examples)
        # 获得文档的置信度
        examples = self.rerank_processor.predict(examples)
        # 计算最终的答案置信度
        examples = self.choose_processor.process(examples)
        examples = self.filter(examples, self.keys)
        return examples

    def predict_v2(self, querys: list, doc: str):
        examples = []
        doc_tokens = list(jieba.cut(doc))
        for index, query in enumerate(querys):
            example = {
                'question_id': index,
                'question': query,
                'doc_tokens': doc_tokens
            }
            examples.append(example)
        examples = self.mrc_processor.predict(examples)
        for example in examples:
            example['answer'] = self.choose_processor.clean_answer(example['answer'])
        examples = self.filter(examples, self.keys)
        return examples

    def predict_v3(self, query: str, docs: list):
        examples = []
        for index, doc in enumerate(docs):
            doc_tokens = list(jieba.cut(doc))
            example = {
                'question_id': index,
                'question': query,
                'doc_tokens': doc_tokens
            }
            examples.append(example)
        examples = self.mrc_processor.predict(examples)
        for example in examples:
            example['answer'] = self.choose_processor.clean_answer(example['answer'])
            example['final_prob'] = example['mrc_prob']
            example['final_prob_v1'] = example['mrc_prob_v1']
            
        examples = sorted(examples, key=lambda x: x['final_prob'], reverse=True)
        examples = self.filter(examples, self.keys)
        return examples


if __name__ == "__main__":
    app = Flask(__name__)
    CORS(app, supports_credentials=True)

    parser = argparse.ArgumentParser()
    parser.add_argument("--config_path", default=None, type=str, required=True,
                        help="config json")
    parser.add_argument("--port", default=None, type=int, required=True,
                        help="config json")
    args = parser.parse_args()

    D = Demo(args.config_path)

    @app.route('/api/chat', methods=['POST', 'GET'])
    def func1():
        try:
            if request.method == 'POST':
                inputs = request.get_json()
                query = inputs['message']
            else:
                query = request.args.get('query')
            return json.dumps({'code': 0, 'results': D.predict(query)}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({'code': 1, 'messge': str(e)})

    @app.route('/api/doc', methods=['POST'])
    def func2():
        try:
            if request.method == 'POST':
                inputs = request.get_json()
                querys = inputs['query']
                doc = inputs['doc']
            return json.dumps({'code': 0, 'results': D.predict_v2(querys, doc)}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({'code': 1, 'messge': str(e)})

    @app.route('/api/doc_qa', methods=['POST'])
    def func3():
        try:
            if request.method == 'POST':
                inputs = request.get_json()
                query = inputs['query']
                docs = inputs['docs']
            return json.dumps({'code': 0, 'results': D.predict_v3(query, docs)}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({'code': 1, 'messge': str(e)})


    app.run(host="127.0.0.1", port=args.port, threaded=True)
