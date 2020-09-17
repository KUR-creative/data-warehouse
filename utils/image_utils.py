from typing import Union
from pathlib import Path

import cv2
import filetype
import imagesize


def assert_img_path(path):
    kind = filetype.guess(str(path))
    assert kind is not None, f'filetype.guess({path}) = {kind}'
    assert kind.mime.split('/')[0] == 'image', \
        f'filetype.guess({path}) = {kind} != image/*'
    return path

def is_img_path(path):
    kind = filetype.guess(str(path))
    return(kind is not None
       and kind.mime.split('/')[0] == 'image')

def img_hw(path):
    w, h = imagesize.get(assert_img_path(path))
    assert w != -1 and h != -1, f"Can't calc img size of {path}"
    return h, w
    
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
