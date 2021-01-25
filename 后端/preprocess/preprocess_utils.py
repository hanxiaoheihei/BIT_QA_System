# -*- coding: utf-8 -*-
# @Time : 2019-10-02 15:12
# @Author : Hongyu Liu
# @Email :liuhongyu12138@gmail.com
# @File : preprocess_utils.py

import time
import sys
import json
import copy
from collections import Counter
import argparse
from tqdm import tqdm

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


def compute_paragraph_score(sample):
    """
    For each paragraph, compute the f1 score compared with the question
    对于每个文档的每个段落，计算其与问题的f1值
    Args:
        sample: a sample in the dataset.
    Returns:
        None
    Raises:
        None
    """
    question = sample["segmented_question"]
    # 拿到问题分词
    for doc in sample['documents']:
        # 对于每一个文档
        doc['segmented_paragraphs_scores'] = []
        # 文档的每个段落得分[第一个段落得分, 第二个段落得分...]
        for p_idx, para_tokens in enumerate(doc['segmented_paragraphs']):
            # para_tokens 当前段落分词
            if len(question) > 0:
                # 如果有问题，算段落分词和问题分词的f1值
                # print(para_tokens)
                # print(question)
                related_score = metric_max_over_ground_truths(f1_score,
                                                              para_tokens,
                                                              [question])
                # print(related_score)
            else:
                related_score = 0.0
            doc['segmented_paragraphs_scores'].append(related_score)
            # 记录


def dup_remove(doc):
    """
    删除当前文档中重复的段落
    For each document, remove the duplicated paragraphs
    Args:
        doc: a doc in the sample
    Returns:
        bool
    Raises:
        None
    """
    paragraphs_his = {}
    del_ids = []
    para_id = None
    if 'most_related_para' in doc:
        para_id = doc['most_related_para']
    # para_id = 最相关段落下标
    doc['paragraphs_length'] = []
    for p_idx, (segmented_paragraph, paragraph_score) in \
            enumerate(zip(doc["segmented_paragraphs"], doc["segmented_paragraphs_scores"])):
        # 拿到段落下标，段落分词，段落对应得分
        doc['paragraphs_length'].append(len(segmented_paragraph))
        # 记录每个段落的长度
        paragraph = ''.join(segmented_paragraph)
        # 将段落分词变成段落
        if paragraph in paragraphs_his:
            # 如果段落出现过，说明重复
            del_ids.append(p_idx)
            # 记录要删除的段落下标
            # if p_idx == para_id:
                # 如果要删除的段落id=最相关段落的id
                # para_id = paragraphs_his[paragraph]
                # 更新最相关段落的id
            continue
        paragraphs_his[paragraph] = p_idx
        # 构造 段落 id 的字典
    # delete
    prev_del_num = 0
    del_num = 0
    for p_idx in del_ids:
        # 拿到每个待删除段落的id
        # if p_idx < para_id:
        #     prev_del_num += 1
        del doc["segmented_paragraphs"][p_idx - del_num]
        del doc["segmented_paragraphs_scores"][p_idx - del_num]
        del doc['paragraphs_length'][p_idx - del_num]
        del_num += 1
    if len(del_ids) != 0:
        if 'most_related_para' in doc:
            doc['most_related_para'] = para_id - prev_del_num
            pass
        doc['paragraphs'] = []
        for segmented_para in doc["segmented_paragraphs"]:
            paragraph = ''.join(segmented_para)
            doc['paragraphs'].append(paragraph)
        return True
    else:
        return False


def paragraph_selection(sample, mode, MAX_P_LEN, topN):
    """
    对于sample每一个文档，选择特别牛逼的那个段落！
    For each document, select paragraphs that includes as much information as possible
    Args:
        sample: a sample in the dataset.
        mode: string of ("train", "dev", "test"), indicate the type of dataset to process.
    Returns:
        None
    Raises:
        None
    """
    # predefined maximum length of paragraph
    # 段落的最大长度为500
    doc_id = None
    if 'answer_docs' in sample and len(sample['answer_docs']) > 0:
        # 如果有answer_docs
        doc_id = sample['answer_docs'][0]
        # 拿到fake_answer对应的那篇文档
        if doc_id >= len(sample['documents']):
            # Data error, answer doc ID > number of documents, this sample
            # will be filtered by dataset.py
            return
    for d_idx, doc in enumerate(sample['documents']):
        # 对于每一个文档
        if 'segmented_paragraphs_scores' not in doc:
            continue
        status = dup_remove(doc)
        # 删除文档中重复的段落
        segmented_title = doc["segmented_title"]
        # 拿到标题的分词
        title_len = len(segmented_title)
        # 拿到标题的长度
        para_id = None
        if doc_id is not None:
            para_id = sample['documents'][doc_id]['most_related_para']
            # fake_answer所在那个段落
        total_len = title_len + sum(doc['paragraphs_length'])
        # 拿到标题+所有段落的总长度
        # add splitter
        para_num = len(doc["segmented_paragraphs"])
        # 当前文档段落总数
        # total_len += para_num
        # 算上了分隔符之后的总长度
        if total_len <= MAX_P_LEN:
            # 如果总长度小于定义的最大长度
            incre_len = title_len
            total_segmented_content = copy.deepcopy(segmented_title)
            # 标题分词
            for p_idx, segmented_para in enumerate(doc["segmented_paragraphs"]):
                # 每一个段落id，每个段落分词
                if doc_id == d_idx and para_id > p_idx:
                    # 如果当前文档是fake_answer文档，且当前段落在fake_answer段落前
                    incre_len += len(segmented_para)
                    # 增量长度 += 1 + 当前长度
                if doc_id == d_idx and para_id == p_idx:
                    # 如果当前文档是fake_answer文档，且当前段落是fake_answer段落
                    incre_len += 0
                    # 增量长度 += 1 (分隔符)
                total_segmented_content += segmented_para
                # total_segmented_content 【增量后的内容】，标题 分隔符 段落...
            if doc_id == d_idx:
                # 如果当前文档是fake_answer文档
                answer_start = incre_len + sample['answer_spans'][0][0]
                # 全局answer start
                answer_end = incre_len + sample['answer_spans'][0][1]
                # 全局answer end
                sample['answer_spans'][0][0] = answer_start
                sample['answer_spans'][0][1] = answer_end
            doc["segmented_paragraphs"] = [total_segmented_content]
            # 这个字段 [[全部内容,合并成一个段落 分词]]
            doc["segmented_paragraphs_scores"] = [1.0]
            #
            doc['paragraphs_length'] = [total_len]
            # 这个字段 段落长度
            doc['paragraphs'] = [''.join(total_segmented_content)]
            # 这个字段 [全部内容，合并成一个段落]
            doc['most_related_para'] = 0
            # 最相关段落，只有一个段落，肯定是这个啦
            # 文档连接后小于MAX长度的，处理完毕
            continue
        # 文档连接后大于等于MAX
        # find topN paragraph id
        # 找到topN f1值的段落id
        para_infos = []
        # 段落信息list   [段落1, 段落2, 段落3]
        for p_idx, (para_tokens, para_scores) in \
                enumerate(zip(doc['segmented_paragraphs'], doc['segmented_paragraphs_scores'])):
            # 当前段落id,当前段落分词 [],当前段落得分f1值。
            para_infos.append((para_tokens, para_scores, len(para_tokens), p_idx))
            # (段落分词，段落得分，段落长度，段落下标)
        para_infos.sort(key=lambda x: (-x[1], x[2]))
        # 先得分排序，后按段落长度排序。
        # 得分大的在前头，相同得分的段落长度少的在前头。
        topN_idx = []
        # topN id list
        for para_info in para_infos[:topN]:
            topN_idx.append(para_info[-1])
            # 获得Top N 段落下标
        final_idx = []
        # final_idx
        total_len = title_len
        # 总长度 = 标题长度
        if doc_id == d_idx:
            # 如果当前文档是fake_answer所在文档
            if mode == "train":
                # 如果是训练集
                final_idx.append(para_id)
                # final_idx 加入 fake_answer所在段落
                total_len = title_len + doc['paragraphs_length'][para_id]
                # 总长度 = 标题长度 + sep + fake_answer所在段落的段落长度
        for id in topN_idx:
            # 对于topN的段落
            if total_len > MAX_P_LEN:
                # 如果当前长度已经大于预设长度，结束！
                break
            if doc_id == d_idx and id == para_id and mode == "train":
                # 当前文档是fake_answer文档,当前段落是fake_answer段落,
                # 且是训练集（那就已经加过了 不用再加啦）
                continue
            total_len += doc['paragraphs_length'][id]
            # 加入当前段落的长度
            final_idx.append(id)
            # 将段落id加入final_idx
        total_segmented_content = copy.deepcopy(segmented_title)
        # total_segmented_content = 标题分词
        final_idx.sort()
        # 按升序排列（按段落先后）
        incre_len = title_len
        for id in final_idx:
            if doc_id == d_idx and id < para_id:
                # 文档是fake_answer所在文档, 选取的段落在fake_answer所在段落前
                incre_len += doc['paragraphs_length'][id]
                # 增量
            if doc_id == d_idx and id == para_id:
                incre_len += 0
                # 增量
            total_segmented_content += doc['segmented_paragraphs'][id]
            # 把选择的段落加进来！
        if doc_id == d_idx:
            # 如果当前文档是fake_answer文档
            answer_start = incre_len + sample['answer_spans'][0][0]
            # 修改区间
            answer_end = incre_len + sample['answer_spans'][0][1]
            sample['answer_spans'][0][0] = answer_start
            sample['answer_spans'][0][1] = answer_end
        doc["segmented_paragraphs"] = [total_segmented_content]
        # [[选择的大段落]]
        doc["segmented_paragraphs_scores"] = [1.0]
        # []
        doc['paragraphs_length'] = [total_len]
        # print(total_len)
        # 段落长度[265]
        doc['paragraphs'] = [''.join(total_segmented_content)]
        # print(len(total_segmented_content))
        # 段落[选择的大段落]
        doc['most_related_para'] = 0
        # 最相关那肯定是第一段啦


def main():
    """
    "do_clean": if do clean, the scripts will remove the example whose fakeanswer not match answer span
    """
    parser = argparse.ArgumentParser()

    ## Required parameters
    parser.add_argument("--data_file", default=None, type=str, required=True,
                        help="Duqa origin json.")
    parser.add_argument("--output_file", default=None, type=str, required=True,
                        help="Duqa preprocessed json")
    parser.add_argument("--eval", action='store_true',
                        help="Whether to eval.")
    parser.add_argument("--output", action='store_true',
                        help="Whether to output.")
    parser.add_argument("--check", action='store_true',
                        help="Whether to check.")
    parser.add_argument("--mode", default=None, type=str, required=True,
                        help="train/dev/test")
    parser.add_argument("--maxp", default=None, type=int, required=True,
                        help="")
    parser.add_argument("--topn", default=None, type=int, required=True,
                        help="")
    parser.add_argument("--do_clean", action='store_true',
                        help="Whether to do clean.")                              
    args = parser.parse_args()

    if args.eval:
        print("evaluate...")
    if args.output:
        print("output...")
    if args.check:
        print("checking...")  
    
    stime = time.time()
    total_num = 0
    answer_num = 0
    answer_not_match = 0

    with open(args.data_file, encoding='utf-8') as f:
        if args.output:
            f_output = open(args.output_file, 'w', encoding='utf-8')
        max_recall_list = []
        passage_tokens_len_list = []
        for line in tqdm(f, desc="processing..."):
            total_num += 1
            if args.output:
                preprocessed_sample = {}
            sample = json.loads(line)
            compute_paragraph_score(sample)
            # 现在每一个文档的每一个段落 都有自己与问题f1值
            # 'segmented_paragraphs_scores' list of list

            # 最重要！
            try:
                paragraph_selection(sample, args.mode, args.maxp, args.topn)
            except:
                answer_not_match += 1
                continue       

            # 答案文档 num
            try:
                answer_doc = sample['answer_docs'][0]
            except:
                answer_doc = 0

            try:
                sample['passage_tokens'] = [sample['documents'][answer_doc]['segmented_paragraphs'][0]]
            except:
                sample['passage_tokens'] = [""]

            if args.mode == 'train' and args.do_clean:
                """
                对于训练集，脚本会自动剔除 answer_doc[span[0]:span[1]] != fake_answer 的训练样本
                对于开发集、测试集则不会
                """
                try:
                    answer_text = sample['documents'][answer_doc]['segmented_paragraphs'][0]
                    fake_answers = sample['fake_answers']
                    answer_spans = sample['answer_spans'][0]
                    answers = "".join(answer_text[answer_spans[0]: answer_spans[1] + 1])
                    if fake_answers[0] != answers:
                        answer_not_match += 1
                        continue
                except:
                    answer_not_match += 1
                    continue

            if args.eval:
                try:
                    max_recall = evaluate_passage_rank(sample)
                except:
                    continue
                if max_recall:
                    max_recall_list.append(max_recall)
                    passage_tokens_len_list.append(len([word for para in sample['passage_tokens'] for word in para]))

            if args.output:
                try:
                    preprocessed_sample['question'] = sample['question']
                    preprocessed_sample['question_id'] = sample['question_id']
                    preprocessed_sample['doc_tokens'] = [word for para in sample['passage_tokens'] for word in para]
                    preprocessed_sample['doc_tokens_len'] = len(preprocessed_sample['doc_tokens'])
                    if args.mode == "train":
                        preprocessed_sample['fake_answer'] = sample['fake_answers']
                        preprocessed_sample['answer_span'] = sample['answer_spans'][0]

                    f_output.write(json.dumps(preprocessed_sample, ensure_ascii=False) + '\n')
                except Exception as e:
                    pass


        if args.eval:
            print("总问题数量: {}".format(total_num))
            print("问题数量：{}".format(len(max_recall_list)))
            print("选取段落平均长度：{}".format(sum(passage_tokens_len_list) / len(passage_tokens_len_list)))
            print("选取段落最大长度：{}".format(max(passage_tokens_len_list)))
            print("选取段落最小长度：{}".format(min(passage_tokens_len_list)))
            print("选取passage平均max_recall：{}".format(sum(max_recall_list) / len(max_recall_list)))
            if args.mode == "train":
                print("No matching exampls：{}".format(answer_not_match))
            print("用时：{}秒".format(time.time() - stime))

        if args.output:
            f_output.close()

        if args.check:
            num = 0
            with open(args.output_file, encoding='utf-8') as f_check:
                for line in f_check:
                    num += 1
            print("输出问题数量: {}".format(num))          


if __name__ == "__main__":
    main()
