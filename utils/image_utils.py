from typing import Union
from pathlib import Path

import cv2

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
