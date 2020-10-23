from typing import Union
from pathlib import Path

import cv2
import filetype
import imagesize
import numpy as np


def assert_img_path(path):
    kind = filetype.guess(str(path))
    assert kind is not None, f'filetype.guess({path}) = {kind}'
    assert kind.mime.split('/')[0] == 'image', \
        f'filetype.guess({path}) = {kind} != image/*'
    return path

def type_str(file_type):
    return '' if file_type is None else file_type.mime
def is_img_type(type): # type from filetype
    return(type is not None
       and type.mime.split('/')[0] == 'image')

def is_img_path(path):
    kind = filetype.guess(str(path))
    return is_img_type(kind)
    #return(kind is not None and kind.mime.split('/')[0] == 'image')

def img_hw(path):
    w, h = imagesize.get(assert_img_path(path))
    assert w != -1 and h != -1, f"Can't calc img size of {path}"
    return h, w
    
def pad(img, h, w, mode='reflect', **kwargs):
    ''' Pad (small) (ih,iw) img to (h,w) img '''
    ih = img.shape[0]; iw = img.shape[1]
    padding = [
        (0,h - ih), (0,w - iw)
    ] + [(0,0)] if len(img.shape) == 3 else []
    
    if mode == 'crop_maximum':
        return np.pad(img, padding, mode='constant',
                      constant_values=np.max(img))
    '''
    elif mode == 'crop_minimum':
        return np.pad(img, padding, mode='constant',
                      constant_values=np.min(img))
    '''
    return np.pad(img, padding, mode=mode)

def crop(img, y, x, h, w, pad_mode, **kwargs):
    ''' If img[y:, x:] is smaller than (h,w), pad applied '''
    return pad(img[y:y+h, x:x+w], h, w, pad_mode, **kwargs)

#---------------------------------------------------------------
class cv:
    @staticmethod
    def read_rgb(path: Union[str, Path]):
        return cv2.cvtColor(cv2.imread(str(path)),
                            cv2.COLOR_BGR2RGB)
    @staticmethod
    def write_rgb(path: Union[str, Path], rgb_img):
        return cv2.imwrite(
            str(path), cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR))
    
    @staticmethod
    def write_png1bit(path: Union[str, Path], mask):
        assert Path(path).suffix == '.png'
        return cv2.imwrite(
            str(path), mask, [cv2.IMWRITE_PNG_BILEVEL, 1])
