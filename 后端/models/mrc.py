# The following classes are added by BIT_OpenDomain_QA team
# @Time : 2019-09-30 13:48
# @Author : Mucheng Ren, Ran Wei, Hongyu Liu, Yu Bai, Yang Wang
# @Email : rdoctmc@gmail.com, weiranbit@163.com, liuhongyu12138@gmail.com, Wnwhiteby@gamil.com, wangyangbit1@gmail.com

import torch
from torch import nn
from torch.nn import CrossEntropyLoss, MSELoss

from transformers.file_utils import add_start_docstrings
from transformers.modeling_bert import (BERT_INPUTS_DOCSTRING,
                                        BERT_START_DOCSTRING, BertModel,
                                        BertPreTrainedModel)

@add_start_docstrings("""Bert Model with a span classification head on top for extractive question-answering tasks like Duqa (a linear layers on top of
    the hidden-states output to compute `span start logits` and `span end logits`). """,
    BERT_START_DOCSTRING, BERT_INPUTS_DOCSTRING)
class BertForBaiduQA_Answer_Selection(BertPreTrainedModel):
    """ TBD """
    def __init__(self, config):
        super(BertForBaiduQA_Answer_Selection, self).__init__(config)
        self.bert = BertModel(config)
        self.qa_outputs = nn.Linear(config.hidden_size, 2)

        self.init_weights()
    
    def forward(self, input_ids, attention_mask=None, token_type_ids=None, position_ids=None, head_mask=None,
                start_positions=None, end_positions=None):

        outputs = self.bert(input_ids,
                            attention_mask=attention_mask,
                            token_type_ids=token_type_ids,
                            position_ids=position_ids, 
                            head_mask=head_mask)
        
        sequence_output = outputs[0]

        logits = self.qa_outputs(sequence_output)
        start_logits, end_logits = logits.split(1, dim=-1)
        start_logits = start_logits.squeeze(-1)
        end_logits = end_logits.squeeze(-1)

        outputs = (start_logits, end_logits,) + outputs[2:]
        if start_positions is not None and end_positions is not None:
            # If we are on multi-GPU, split add a dimension
            if len(start_positions.size()) > 1:
                start_positions = start_positions.squeeze(-1)
            if len(end_positions.size()) > 1:
                end_positions = end_positions.squeeze(-1)
            # sometimes the start/end positions are outside our model inputs, we ignore these terms
            ignored_index = start_logits.size(1)
            start_positions.clamp_(0, ignored_index)
            end_positions.clamp_(0, ignored_index)

            loss_fct = CrossEntropyLoss(ignore_index=ignored_index)
            start_loss = loss_fct(start_logits, start_positions)
            end_loss = loss_fct(end_logits, end_positions)
            total_loss = (start_loss + end_loss) / 2
            outputs = (total_loss,) + outputs

        return outputs  # (loss), start_logits, end_logits, (hidden_states), (attentions)
