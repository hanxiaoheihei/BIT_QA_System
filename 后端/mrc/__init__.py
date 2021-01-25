# -*- coding: utf-8 -*-

# @Time : 2019-10-06 12:35
# @Author : rwei
# @Email : weiranbit@163.com
# @File : __init__.py

from .run_duqa import MODEL_CLASSES as mrc_MODEL_CLASSES
from .run_duqa import predict as mrc_predict # for server
from .run_duqa import evaluate as mrc_evaluate
from .run_duqa import set_seed, to_list
from .run_duqa import main as mrc_train