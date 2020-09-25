'''
fmap image root. 
Apply a mapping func f to all imgs from src_root,
And then generate pairs of (src_img, dst_path)
'''
from pathlib import Path

import funcy as F

from utils import file_utils as fu
from utils import fp
from utils import image_utils as iu

import core
import core.path
import core.crops

def mask1bit_dstpath_pairseq(src_root, dst_root=None, which=0):
    ''' 
    Generate <[1bit-mask, dst-path]>.
    
    1bit means 0/1 mask. Actual dtype is 'uint8'.
    
    dst_root is root directory path to save generated crops.
    If None, dst_root is '{src_root}.ch{which}'
    
    which is channel of image to extract. 
    0 means red channel(in rgb scheme).
    
    ex) src_root = ../SZMC_DATA/masks, dst_root = None, which=0
     => dst_root = ../SZMC_DATA/masks.ch0
    '''
    if dst_root is None:
        src = str(Path(src_root)) # Remove path sep thingy
        dst_root = f'{src}.ch{which}'
    src_paths, raw_dst_paths = fp.unzip(
        fu.copy_path_pairs(src_root, dst_root))
    
    maskseq = (iu.cv.read_rgb(p)[:,:,which].astype(bool)
                                           .astype('uint8')
               for p in src_paths)
    dst_pathseq = (str(Path(p).with_suffix('.png'))
                   for p in raw_dst_paths)
    return zip(maskseq, dst_pathseq)

def recur_cropseq(img_root, dst_root, crop_h, crop_w,
                  pad_mode, **kwargs):
    ''' 
    Return (len, cropseq, dst_pathseq) 
    kwargs for np.pad
    '''
    ch, cw = crop_h, crop_w
    assert Path(img_root).exists()
    assert Path(img_root).is_dir()
    img_root = Path(img_root)
    dst_root = Path(dst_root)
    
    src_paths, dst_img_paths = fp.unzip(
        fu.copy_path_pairs(img_root, dst_root))

    yxs_lst = [
        core.crops.yxs(*iu.img_hw(src_path), crop_h, crop_w)
        for src_path in src_paths]
    
    imgseq = (iu.cv.read_rgb(p) for p in src_paths)
    cropseq = F.cat(
        (iu.crop(img, y,x, ch,cw,
                 pad_mode, **kwargs) for y,x in yxs)
        for img, yxs in zip(imgseq, yxs_lst))
    crop_pathseq = F.cat(
        (core.path.crop(dst_path, y, x) for y, x in yxs)
        for dst_path, yxs in zip(dst_img_paths, yxs_lst))

    num_mappings = sum(len(yxs) for yxs in yxs_lst)
    return num_mappings, cropseq, crop_pathseq
