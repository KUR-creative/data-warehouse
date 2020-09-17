from itertools import product

from funcy import memoize

from utils.etc_utils import factorseq, modulo_pad


@memoize
def yxs(img_h, img_w, crop_h, crop_w):
    if crop_h > img_h or crop_w > img_w:
        raise ValueError(
            f'{crop_h} > {img_h} or {crop_w} > {img_w}')
    padded_h = img_h + modulo_pad(crop_h, img_h)
    padded_w = img_w + modulo_pad(crop_w, img_w)
    hs = factorseq(crop_h, padded_h)
    ws = factorseq(crop_w, padded_w)
    return [list(tup) for tup in product(hs, ws)]
