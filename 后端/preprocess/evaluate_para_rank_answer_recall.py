# -*- coding: utf-8 -*-
# @Time : 2019-10-02 17:50
# @Author : Hongyu Liu
# @Email :liuhongyu12138@gmail.com 
# @File : preprocess_utils.py

"""
评测段落排序器的脚本
sample：
问题id:int
问题：string
需要的是抽取的passage tokens：list形式
多个参考答案tokens: list of list
"""
import json
from collections import Counter
import time
import random
train_zhidao = 'data/train_preprocessed/train_preprocessed/trainset/zhidao.train.json'
train_search = 'data/train_preprocessed/train_preprocessed/trainset/search.train.json'
dev_zhidao = 'data/dev_preprocessed/dev_preprocessed/devset/zhidao.dev.json'
dev_search = 'data/dev_preprocessed/dev_preprocessed/devset/search.dev.json'


# dev_zhidao_passage = 'output/lhy/dev_zhidao.json'
# dev_search_passage = 'output/lhy/dev_search.json'
dev_dict = {
    'dev_search': 'output/lhy/dev_search.json',
    'dev_zhidao': 'output/lhy/dev_zhidao.json'
}
dev_file = ['dev_search', 'dev_zhidao']
def precision_recall_f1(prediction, ground_truth):
    """
    This function calculates and returns the precision, recall and f1-score
    Args:
        prediction: prediction string or list to be matched
        ground_truth: golden string or list reference
    Returns:
        floats of (p, r, f1)
    Raises:
        None
    """
    if not isinstance(prediction, list):
        prediction_tokens = prediction.split()
    else:
        prediction_tokens = prediction
    if not isinstance(ground_truth, list):
        ground_truth_tokens = ground_truth.split()
    else:
        ground_truth_tokens = ground_truth
    common = Counter(prediction_tokens) & Counter(ground_truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0, 0, 0
    p = 1.0 * num_same / len(prediction_tokens)
    r = 1.0 * num_same / len(ground_truth_tokens)
    f1 = (2 * p * r) / (p + r)
    return p, r, f1


def recall(prediction, ground_truth):
    """
    This function calculates and returns the recall
    Args:
        prediction: prediction string or list to be matched
        ground_truth: golden string or list reference
    Returns:
        floats of recall
    Raises:
        None
    """
    return precision_recall_f1(prediction, ground_truth)[1]


def f1_score(prediction, ground_truth):
    """
    This function calculates and returns the f1-score
    Args:
        prediction: prediction string or list to be matched
        ground_truth: golden string or list reference
    Returns:
        floats of f1
    Raises:
        None
    """
    return precision_recall_f1(prediction, ground_truth)[2]


def metric_max_over_ground_truths(metric_fn, prediction, ground_truths):
    """
    This function calculates and returns the precision, recall and f1-score
    Args:
        metric_fn: metric function pointer which calculates scores according to corresponding logic.
        prediction: prediction string or list to be matched
        ground_truth: golden string or list reference
    Returns:
        floats of (p, r, f1)
    Raises:
        None
    """
    scores_for_ground_truths = []
    for ground_truth in ground_truths:
        score = metric_fn(prediction, ground_truth)
        scores_for_ground_truths.append(score)
    return max(scores_for_ground_truths)


def evaluate_passage_rank(sample):
    """
    计算每个抽取的passage（送给阅读器训练）的答案recall
    sample['question_id'] = 问题id
    sample['question'] = 问题
    sample['passage_tokens'] = 抽取的段落分词 list of list[[抽的第一个段落], [抽的第二个段落]...]
    sample['segmented_answers'] = 答案 list of list [[第一个答案]...]
    :return:
    """
    # 计算抽取的段落和参考答案的max_f1
    question_id = sample['question_id']
    question = sample['question']
    selected_passage_tokens = sample['passage_tokens']
    segmented_answers = sample['segmented_answers']
    related_score_list = []

    for p_idx, para_tokens in enumerate(selected_passage_tokens):
        if len(sample['segmented_answers']) > 0:
            related_score = metric_max_over_ground_truths(recall,
                                                          para_tokens,
                                                          segmented_answers)
            related_score_list.append(related_score)
    if related_score_list:
        sample['related_score_list'] = related_score_list
    return max(related_score_list)


if __name__ == '__main__':
    time_start = time.time()
    for var in dev_file:
        with open(dev_dict[var], encoding='utf-8') as f:
            max_recall_list = []
            passage_tokens_len_list = []
            for line in f:
                sample = json.loads(line)
                try:
                    pass
                    # 一个问题，只选fake answer所在的那一段落，最优解
                    # sample['passage_tokens'] = [sample['documents'][sample['answer_docs'][0]]['segmented_paragraphs'][
                    #     sample['documents'][sample['answer_docs'][0]]['most_related_para']]]

                    # 一个问题 选第一文档的第一段
                    # sample['passage_tokens'] = [sample['documents'][0]['segmented_paragraphs'][0]]

                    # 一个问题 随机选一个段落的随机一段
                    # first = random.randint(0, len(sample['documents'])-1)
                    # second = random.randint(0, len(sample['documents'][first]['segmented_paragraphs'])-1)
                    # sample['passage_tokens'] = [sample['documents'][first]['segmented_paragraphs'][second]]
                    # print(sample['passage_tokens'])

                    # 一个问题 随机选一个段落的随机一段+最优段
                    # first = random.randint(0, len(sample['documents']) - 1)
                    # second = random.randint(0, len(sample['documents'][first]['segmented_paragraphs']) - 1)
                    # first_para = sample['documents'][first]['segmented_paragraphs'][second]
                    # second_para = sample['documents'][sample['answer_docs'][0]]['segmented_paragraphs'][
                    #      sample['documents'][sample['answer_docs'][0]]['most_related_para']]
                    # sample['passage_tokens'] = [first_para, second_para]
                    # print(sample['passage_tokens'])
                    # sample
                except IndexError:
                    continue
                max_recall = evaluate_passage_rank(sample)
                if max_recall:
                    # print(match_score)
                    # print(sample['match_scores'][0])
                    # print(fake_answer)
                    # print(sample['fake_answers'][0])
                    # print(sample['related_score_list'])
                    max_recall_list.append(max_recall)
                    passage_tokens_len_list.append(len([word for para in sample['passage_tokens'] for word in para]))
                    # print(len(max_recall_list))
                # break
                # if len(max_recall_list) % 100 == 0:
                #     print("问题数量：{}".format(len(max_recall_list)))
                #     print("选取段落平均长度：{}".format(sum(passage_tokens_len_list) / len(passage_tokens_len_list)))
                #     print("选取段落最大长度：{}".format(max(passage_tokens_len_list)))
                #     print("选取段落最小长度：{}".format(min(passage_tokens_len_list)))

                #     print("选取段落平均match_score：{}".format(sum(max_recall_list) / len(max_recall_list)))

                #     print("用时：{}秒".format(time.time() - time_start))
                #     print('\n')
                    # break

        # print(passage_tokens_len_list)
        print(var + ': ')
        print("问题数量：{}".format(len(max_recall_list)))
        print("选取段落平均长度：{}".format(sum(passage_tokens_len_list) / len(passage_tokens_len_list)))
        print("选取段落最大长度：{}".format(max(passage_tokens_len_list)))
        print("选取段落最小长度：{}".format(min(passage_tokens_len_list)))

        print("选取passage平均max_recall：{}".format(sum(max_recall_list) / len(max_recall_list)))

        print("用时：{}秒".format(time.time() - time_start))
