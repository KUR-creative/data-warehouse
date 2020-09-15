from pathlib import Path

from utils import file_utils as fu
from utils import fp
from utils import image_utils as iu

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
    dst_pathseq = (Path(p).with_suffix('.png')
                   for p in raw_dst_paths)
    return zip(maskseq, dst_pathseq)
