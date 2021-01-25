# -*- coding: utf-8 -*-
""" Load Duqa labeled dataset. """

from __future__ import absolute_import, division, print_function

import collections
import json
import logging
import math
from io import open

from tqdm import tqdm

from transformers.tokenization_bert import BasicTokenizer, whitespace_tokenize

logger = logging.getLogger(__name__)


class InputExample(object):
    """A single training/test example for simple sequence classification."""

    def __init__(self, guid, text_a, text_b=None, label=None):
        """Constructs a InputExample."""
        self.guid = guid
        self.text_a = text_a
        self.text_b = text_b
        self.label = label


class InputFeatures(object):
    """A single set of features of data."""

    def __init__(self, input_ids, input_mask, segment_ids, label_id):
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.segment_ids = segment_ids
        self.label_id = label_id


class DataProcessor(object):
    """Base class for data converters for sequence classification data sets."""

    def get_train_examples(self, data_dir):
        """Gets a collection of `InputExample`s for the train set."""
        raise NotImplementedError()

    def get_dev_examples(self, data_dir):
        """Gets a collection of `InputExample`s for the dev set."""
        raise NotImplementedError()

    def get_labels(self):
        """Gets the list of labels for this data set."""
        raise NotImplementedError()

    @classmethod
    def _read_json_data(cls, input_file):
        """Read a json file"""
        lines = list(open(input_file, 'r', encoding='utf8').readlines())
        lines = [json.loads(line) for line in lines]
        return lines


class DuQAProcessor(DataProcessor):
    """Processor for the DuReader data set:"""

    def get_train_examples(self, data_dir):
        """See base class."""
        logger.info("LOOKING AT {}".format(os.path.join(data_dir, "train_labeled.json")))
        return self._create_examples(self._read_json_data(os.path.join(data_dir, "train_labeled.json")), "train")

    def get_dev_examples(self, data_dir):
        """See base class."""
        return self._create_examples(self._read_json_data(os.path.join(data_dir, "dev_labeled.json")), "dev")

    def get_predict_examples(self, examples):
        """ get predict examples 
        Args:
            data_file: list include many json
        """
        return self._create_examples(examples, "infer")
    
    def get_labels(self):
        """
        - 0：not_most_related
        - 1: most_related
        """

        return [0, 1]

    def _create_examples(self, examples, set_type):
        """
        here we input a example list:
        [
            {
                "question_id": int,
                "question": string,
                "doc_tokens": string,
                "mrc_logits": float,
                "answer":sring,
            }
        
        """
        examples_list = []

        for id, example in enumerate(examples):
            guid = set_type + '-' + str(id)
            text_a = example['question']
            text_b = example['answer']           
            label = 0 ## 在predict环节这里没用，只是一个tag
            examples_list.append(
                InputExample(
                    guid=guid,
                    text_a=text_a,
                    text_b=text_b,
                    label=label
                )
            )
        return examples_list


def convert_examples_to_features(examples, label_list, max_seq_length, tokenizer):
    label_map = {label : i for i, label in enumerate(label_list)}
    
    features = []
    for (ex_index, example) in tqdm(enumerate(examples), desc='loading_data'):
        tokens_a = tokenizer.tokenize(example.text_a)

        tokens_b = None
        if example.text_b:
            tokens_b = tokenizer.tokenize(example.text_b)
            _truncate_seq_pair(tokens_a, tokens_b, max_seq_length - 3)
        else:
            if len(tokens_a) > max_seq_length - 2:
                tokens_a = tokens_a[:(max_seq_length - 2)]

        tokens = ["[CLS]"] + tokens_a + ["[SEP]"]
        segment_ids = [0] * len(tokens)

        if tokens_b:
            tokens += tokens_b + ["[SEP]"]
            segment_ids += [1] * (len(tokens_b) + 1)
        
        input_ids = tokenizer.convert_tokens_to_ids(tokens)
        input_mask = [1] * len(input_ids)

        padding = [0] * (max_seq_length - len(input_ids))
        input_ids += padding
        input_mask += padding
        segment_ids += padding

        assert len(input_ids) == max_seq_length
        assert len(input_mask) == max_seq_length
        assert len(segment_ids) == max_seq_length

        label_id = label_map[example.label]
        # if ex_index < 5:
        #     logger.info("*** Example ***")
        #     logger.info("guid: %s" % (example.guid))
        #     logger.info("tokens: %s" % " ".join(
        #             [str(x) for x in tokens]))
        #     logger.info("input_ids: %s" % " ".join([str(x) for x in input_ids]))
        #     logger.info("input_mask: %s" % " ".join([str(x) for x in input_mask]))
        #     logger.info(
        #             "segment_ids: %s" % " ".join([str(x) for x in segment_ids]))
        #     logger.info("label: %s (id = %d)" % (example.label, label_id))

        features.append(
                InputFeatures(input_ids=input_ids,
                              input_mask=input_mask,
                              segment_ids=segment_ids,
                              label_id=label_id))
    return features


def _truncate_seq_pair(tokens_a, tokens_b, max_length):
    """Truncates a sequence pair in place to the maximum length."""

    # This is a simple heuristic which will always truncate the longer sequence
    # one token at a time. This makes more sense than truncating an equal percent
    # of tokens from each, since if one sequence is very short then each token
    # that's truncated likely contains more information than a longer sequence.
    while True:
        total_length = len(tokens_a) + len(tokens_b)
        if total_length <= max_length:
            break
        if len(tokens_a) > len(tokens_b):
            tokens_a.pop()
        else:
            tokens_b.pop()


processors = {
    'duqa': DuQAProcessor,
}


num_labels_task = {
    'duqa': 2,
}
