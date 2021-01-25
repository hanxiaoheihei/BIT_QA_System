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
import numpy as np
import torch
from torch.utils.data import (DataLoader, RandomSampler, SequentialSampler,
                              TensorDataset)
from torch.utils.data.distributed import DistributedSampler
from tqdm import tqdm, trange

from creeper import creeper_v1, creeper_v2
from flask import Flask, jsonify, request
from flask_restful import Api, Resource, reqparse
from mrc import mrc_evaluate, mrc_MODEL_CLASSES, mrc_predict, set_seed, to_list
from rerank import rerank_MODEL_CLASSES, rerank_predict

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt='%m/%d/%Y %H:%M:%S',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

class Args(object):
    def __init__(self, config):
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
        args.model_name_or_path = os.path.join(args.model_name_or_path, "checkpoint-{}".format(args.checkpoint_id))
        args.output_dir = os.path.join(args.output_dir, "checkpoint-{}".format(args.checkpoint_id))

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

    def evaluate(self):
        mrc_evaluate(self.args, self.model, self.tokenizer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint_id", default='0', type=str)
    args = parser.parse_args()

    eval_config = json.load(open('eval_config.json', 'r'))
    eval_config["mrc"]["checkpoint_id"] = args.checkpoint_id
    eval_processor = Mrc(eval_config)
    eval_processor.evaluate()
