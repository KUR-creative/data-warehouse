import os
from pathlib import Path

import numpy as np
from tqdm import tqdm

from tasks import gen_crops
from utils import fp 
from utils import file_utils as fu
from utils import etc_utils as etc
from utils import image_utils as iu


def generate_crops(data_source, h, w, pages='*'): # TODO: refactor
    '''
    '*' means all pages 
    '''
    if pages == '*':
        raise NotImplementedError(
            "Currently only pages: List[int] is supported")
    # Get src images
    DATA_dir = Path(data_source, 'DATA')
    img_root_dir = Path(DATA_dir, 'images')
    
    paths = [Path(p) for p in fu.descendants(img_root_dir)]
    selected_paths = fp.lfilter(
        lambda p: int(p.stem.split('_')[-1]) in pages, paths)
    #pprint(selected_paths)
    
    title_paths = fp.group_by(
        lambda p: p.parent.stem, selected_paths)
    dst_crops_dir = Path(
        DATA_dir,
        'crop',
        'pp' + etc.sjoin('_', pages) + f'.h{h}w{w}.h_pad')
    #print(dst_crops_dir)
    for title, paths in tqdm(title_paths.items()):
        _gen_crops(DATA_dir, paths, h, w, dst_crops_dir / title)

    
def _gen_crops(DATA_dir, img_paths, h, w, dst_crops_dir):
    '''
    NOTE: height가 짧다면를 h가 되도록 패딩을 한다.
    
    DATA_dir: 데이터 소스의 DATA 디렉토리 경로
    img_path: 자르려는 이미지의 경로
    h, w: 잘려져 나오는 crop의 크기
    dst_crops_dir: crop이 저장되는 디렉토리 경로
    '''
    # Generate (path, crop)s
    path_crop_seq = gen_crops.do(img_paths, h, w, dst_crops_dir)
    
    # Pad to 256 for short height image
    def hpad(img, h, w, mode='reflect'):
        ih = img.shape[0]; #iw = img.shape[1]
        padding = [
            #(0,h_padding), (0,w_padding)
            (0,h - ih), (0,0)
        ] + [(0,0)] if len(img.shape) == 3 else []
        return np.pad(img, padding, mode=mode)
    
    # look & feel check (and count crops)
    '''
    num = 0
    for p, c in path_crop_seq:
        print(dst_crops_dir, p, c.shape);
        cv2.imshow('c',hpad(c, h, w)); cv2.waitKey(0)
        num += 1
    return num
    '''
    
    # Save to dst directories
    os.makedirs(dst_crops_dir, exist_ok=True)
    # TODO: makedirs parents.. preserve directory structure.
    
    for path, crop in path_crop_seq:
        iu.cv.write_rgb(path, hpad(crop, h, w))
