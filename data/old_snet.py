import os
from pathlib import Path

import numpy as np
from tqdm import tqdm

from tasks import gen_crops
from utils import fp 
from utils import file_utils as fu
from utils import image_utils as iu

def generate_crops(data_source, h, w): # TODO: refactor
    # Get src images
    DATA_dir = Path(data_source, 'DATA')
    img_dir = Path(DATA_dir, 'image')
    wk_dir = Path(DATA_dir, 'clean_wk')
    assert img_dir.exists()

    for dir_path in [img_dir, wk_dir]:
        org_paths = fu.descendants(dir_path)
        max_id = max(int(Path(p).stem) for p in org_paths)

        def get10x(n): return (n // 10) * 10
        crop_dir_name = f'{dir_path.stem}.h{h}w{w}'
        crop_dirs = [
            DATA_dir / 'crop' / crop_dir_name / str(n)
            for n in range(0, get10x(max_id) + 10, 10)]
        num2crop_dir = fp.zipdict(
            (int(p.stem) for p in crop_dirs), crop_dirs)

        for dir_path in crop_dirs:
            os.makedirs(dir_path, exist_ok=True)
        for path in tqdm(org_paths,
                         desc=f'Generate {crop_dir_name}'):
            crop_dir = num2crop_dir[ get10x(int(Path(path).stem)) ]
            _gen_crops(DATA_dir, [path], h, w, crop_dir)

def _gen_crops(DATA_dir, img_paths, h, w, dst_crops_dir):
    '''
    NOTE: 크기가 작다면 h,w가 되도록 패딩을 한다.
    
    DATA_dir: 데이터 소스의 DATA 디렉토리 경로
    img_path: 자르려는 이미지의 경로
    h, w: 잘려져 나오는 crop의 크기
    dst_crops_dir: crop이 저장되는 디렉토리 경로
    '''
    # Generate (path, crop)s
    path_crop_seq = gen_crops.do(img_paths, h, w, dst_crops_dir)
    
    # Pad to 256 for short height image
    def pad(img, h, w, mode='reflect'):
        ih = img.shape[0]; iw = img.shape[1]
        padding = [
            (0,h - ih), (0,w - iw)
        ] + [(0,0)] if len(img.shape) == 3 else []
        return np.pad(img, padding, mode=mode)
    
    # look & feel check (and count crops)
    '''
    num = 0
    import cv2
    for p, c in path_crop_seq:
        print(dst_crops_dir, p, c.shape);
        #cv2.imshow('c',pad(c, h, w)); cv2.waitKey(0)
        num += 1
    return num
    '''
    
    for path, crop in path_crop_seq:
        iu.cv.write_rgb(path, pad(crop, h, w))
