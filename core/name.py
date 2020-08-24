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
