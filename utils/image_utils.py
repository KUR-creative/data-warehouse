from typing import Union
from pathlib import Path

import cv2

class cv:
    @staticmethod
    def read_rgb(path: Union[str, Path]):
        return cv2.cvtColor(cv2.imread(str(path)),
                            cv2.COLOR_BGR2RGB)
    @staticmethod
    def write_rgb(path, rgb_img):
        return cv2.imwrite(
            path, cv2.cvtColor(rgb_img, cv2.COLOR_RGB2BGR))
