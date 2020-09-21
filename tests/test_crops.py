import pytest
from hypothesis import assume, given #, example, settings
from hypothesis import strategies as st

import core
import core.crops
from utils.etc_utils import factors, modulo_pad
from utils import fp

@st.composite
def crop_larger_than_img(draw, min_value=28, max_v=4000):
    img_h = draw(st.integers(min_value=min_value, max_value=max_v))
    img_w = draw(st.integers(min_value=min_value, max_value=max_v))
    
    h_error = draw(st.booleans())
    w_error = draw(st.booleans())
    assume(h_error or w_error)
    
    min_h = img_h + 1 if h_error else min_value
    min_w = img_w + 1 if w_error else min_value
    crop_h = draw(st.integers(min_value=min_h))
    crop_w = draw(st.integers(min_value=min_w))
    return (img_h, img_w, crop_h, crop_w)

@st.composite
def crop_normal_args(draw, min_v=28, max_v=4000):
    img_h = draw(st.integers(min_value=min_v, max_value=max_v))
    img_w = draw(st.integers(min_value=min_v, max_value=max_v))
    crop_h = draw(st.integers(min_value=min_v, max_value=img_h))
    crop_w = draw(st.integers(min_value=min_v, max_value=img_w))
    return (img_h, img_w, crop_h, crop_w)

# TODO: Refactor - unite same code as one
@given(crop_larger_than_img())
def test_crops_larger_than_img(args):
    img_h, img_w, crop_h, crop_w = args
    yxs = core.crops.yxs(*args)

    padded_h = img_h + modulo_pad(crop_h, img_h)
    padded_w = img_w + modulo_pad(crop_w, img_w)
    ys, xs = fp.unzip(yxs)
    
    assert len(set(ys)) * crop_h == padded_h
    assert len(set(xs)) * crop_w == padded_w
        
@given(crop_normal_args())
def test_crops(args):
    img_h, img_w, crop_h, crop_w = args
    yxs = core.crops.yxs(*args)

    padded_h = img_h + modulo_pad(crop_h, img_h)
    padded_w = img_w + modulo_pad(crop_w, img_w)
    ys, xs = fp.unzip(yxs)
    
    assert len(set(ys)) * crop_h == padded_h
    assert len(set(xs)) * crop_w == padded_w
