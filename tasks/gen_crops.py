import itertools as I
from pathlib import Path

from funcy import memoize
import imagesize

from utils import fp, image_utils as iu
from utils.etc_utils import factors, modulo_pad

def do(img_paths, crop_h, crop_w, crop_dir):
    ''' 
    crop_dir is directory path to save generated crops. 
    return: <(path, crop)>. crop is rgb (h,w) image.
    '''
    # Make [(fname, extension)]
    stem_ext_lst = (
        (p.stem, p.suffix) for p in map(Path, img_paths))
    # Make <img> img sequence 
    imgseq = (iu.cv.read_rgb(p) for p in img_paths) # TODO: rgba?
    # Make [[(y,x)]] # TODO: refactor to core.crops(h,w,ch,cw)?
    ws, hs = fp.unzip(imagesize.get(p) for p in img_paths)
    hs = (h + _modulo_pad(crop_h, h) for h in hs)
    ws = (w + _modulo_pad(crop_w, w) for w in ws)
    ys_seq = (list(_factors(crop_h, h)) for h in hs)
    xs_seq = (list(_factors(crop_w, w)) for w in ws)
    yxs_lst = fp.lmap(fp.pipe(I.product, list), ys_seq, xs_seq)

    # Make [(path, crop)]
    def crop_paths(stem_ext, yxs):
        stem, ext = stem_ext
        return (str(Path(crop_dir, f'{stem}_y{y}x{x}{ext}'))
                for y, x in yxs)
    def cropseq(img, yxs):
        return (img[y:y+crop_h, x:x+crop_w] for y,x in yxs)
    path_crop_pairseq = zip(
        fp.lmapcat(crop_paths, stem_ext_lst, yxs_lst),
        fp.mapcat(cropseq, imgseq, yxs_lst))
    
    # look & feel check
    #for path, crop in path_crop_pairseq: print(path); print(crop.shape); cv2.imshow('c',crop); cv2.waitKey(0)
    return path_crop_pairseq

#--------------------------------------------------------------
# private functions # TODO: refactor to core.crops(h,w,ch,cw)?
@memoize
def _modulo_pad(crop_size, img_size):
    return modulo_pad(crop_size, img_size)

@memoize
def _factors(crop_size, img_size):
    return factors(crop_size , img_size)
