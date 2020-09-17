from typing import Tuple
import re

from parse import parse


def h_w(h_w_name):
    ''' 
    get h,w from h_w_name = "....h{h}w{w}....". 
    h{h}w{w} must be only one.
    '''
    crop_size_strs = re.findall('h[0-9]+w[0-9]+', h_w_name)
    assert len(crop_size_strs) == 1, f'{len(crop_size_strs)} != 1'
    hw_str = crop_size_strs[0]
    h, w = map(int, parse('h{}w{}', hw_str))
    return h, w

def dset_name(name: str,
              type: str,
              crop_hw: Tuple[int,int],
              revision_rdt: Tuple[int, int, int],
              dset_dic,
              suffix='.yml'):
    h, w = crop_hw
    r_train, r_dev, r_test = revision_rdt
    n_train = sum(len(d['yxs']) for d in dset_dic['TRAIN'])
    n_dev = sum(len(d['yxs']) for d in dset_dic['DEV'])
    n_test = sum(len(d['yxs']) for d in dset_dic['TEST'])
    return '.'.join([name, type, f'h{h}w{w}',
                     f'{r_train}_{n_train}',
                     f'{r_dev}_{n_dev}',
                     f'{r_test}_{n_test}']) + suffix
