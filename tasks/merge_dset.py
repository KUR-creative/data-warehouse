import socket
import sys

import funcy as F
import yaml

from utils import etc_utils as etc


def do(*dset_paths):
    ''' 
    Don't give a shit for meta information.
    
    example: default.merge([path1, path2], [dict1, dict2])
    '''
    dics = []
    for path in dset_paths:
        with open(path) as f:
            dics.append(yaml.safe_load(f))

    for path,dic in zip(dset_paths,dics):
        assert dic.get('TRAIN'), f'{path} has no key: TRAIN'
        assert dic.get('DEV'), f'{path} has no key: DEV'
        assert dic.get('TEST'), f'{path} has no key: TEST'
    # Merge
    train = F.lmapcat(lambda d: d['TRAIN'], dics)
    dev = F.lmapcat(lambda d: d['DEV'], dics)
    test = F.lmapcat(lambda d: d['TEST'], dics)
    # Assert Uniqueness
    assert len(train) == len(set(map(tuple, train)))
    assert len(dev) == len(set(map(tuple, dev)))
    assert len(test) == len(set(map(tuple, test)))
    # Inplace Shuffle 
    #etc.inplace_shuffled(train) # 어차피 실험할 때 섞는다..
    #etc.inplace_shuffled(dev)
    #etc.inplace_shuffled(test)
    
    return dict(
        MERGED_DATASETS = dset_paths,
        DATA_SOURCES = F.lmapcat(
            lambda d: d['DATA_SOURCES'], dics),
        DESCRIPTION = dict(
            WHAT = '기존 dset 여럿을 merge하여 생성한 dset',
            WHY = '더 많은 데이터... 더 큰 모델... 더 높은 정확도..',
            KNOWN_ERRORS = '여러 dset에 존재하는 에러를 합친 정도'),
        CREATION = dict(
            HOST_NAME = socket.gethostname(),
            COMMAND = ' '.join(sys.argv),
            GIT_HASH = etc.git_hash()),
        NUM_TRAIN = len(train),
        NUM_DEV = len(dev),
        NUM_TEST = len(test),
        TRAIN = train,
        DEV = dev,
        TEST = test,
    )
