from itertools import product

from funcy import memoize

from utils.etc_utils import factors, modulo_pad


def yxs(img_h, img_w, crop_h, crop_w):
    if crop_h > img_h or crop_w > img_w:
        raise ValueError(
            f'{crop_h} > {img_h} or {crop_w} > {img_w}')
    padded_h = img_h + _modulo_pad(crop_h, img_h)
    padded_w = img_w + _modulo_pad(crop_w, img_w)
    hs = _factors(crop_h, padded_h)
    ws = _factors(crop_w, padded_w)
    return list(product(hs, ws))

@memoize
def _modulo_pad(crop_size, img_size):
    return modulo_pad(crop_size, img_size)

@memoize
def _factors(crop_size, img_size):
    return factors(crop_size , img_size)
