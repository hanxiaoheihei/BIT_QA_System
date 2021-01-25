from mrc import mrc_train
from rerank import rerank_train

if __name__ == "__main__":
    mode = 'mrc' # mrc or rerank
    if mode == 'mrc':
        mrc_train()
    if mode == 'rerank':
        rerank_train()