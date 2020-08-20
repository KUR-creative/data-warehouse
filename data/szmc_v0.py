import os
from pathlib import Path

import cv2

from tasks import gen_crops
from utils import file_utils as fu


#---------------------------------------------------------------
def save_crops(root, h, w): # TODO: refactor
    # Get src images
    org_dir = Path(root, 'prev_images') 
    mask_dir = Path(root, 'mask1bit')
    _gen_crops(root, org_dir, h, w)
    _gen_crops(root, mask_dir, h, w)

def _gen_crops(root, img_dir, h, w, dst_dir=None):
    # Get src images
    assert img_dir.exists()
    
    crop_dir = Path(root, 'crop')
    dst_crops_dir = crop_dir / f'{img_dir.stem}.h{h}w{w}'
    
    # Generate (path, crop)s
    paths = fu.human_sorted(fu.descendants(img_dir))
    path_crop_seq = gen_crops.do(paths, h, w, dst_crops_dir)
    
    # look & feel check
    '''
    from funcy import take
    for p, c in take(40, path_crop_seq):
        print(' org:', p, c.shape);
        cv2.imshow('c',c);
        cv2.waitKey(0)
    exit()
    '''
    
    # Save to dst directories
    os.makedirs(dst_crops_dir, exist_ok=True)
    # TODO: makedirs parents.. preserve directory structure.
    
    print(f'start: _gen_crops({root}, {img_dir}, {h}, {w}, {dst_dir})')
    for path, crop in path_crop_seq:
        cv2.imwrite(path, cv2.cvtColor(crop, cv2.COLOR_RGB2BGR))
    print('finished')

#---------------------------------------------------------------
