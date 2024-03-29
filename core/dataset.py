from pathlib import Path

from multimethod import overload
import funcy as F

from utils import image_utils as iu
import core
import core.crops

#---------------------------------------------------------------
# Relation Types
def base_relation(inp, out, **attrs):
    return F.merge({'inp': inp, 'out': out}, attrs)

def crop_relation(img, out, img_h, img_w, crop_h, crop_w, yxs,
                  **attrs):
    return F.merge(base_relation(img, out),
                   {'img_h':img_h, 'img_w':img_w,
                    'crop_h':crop_h, 'crop_w':crop_w,
                    'yxs': yxs},
                   attrs)
    
#---------------------------------------------------------------
@overload
def relation(inp, out, crop_h=None, crop_w=None, **attrs):
    ''' 
    Relation of dataset. It represents input:output mapping
    and image:[crop]s mapping. Relations come together to form
    a dataset.
    
    Return dict.
    
    inp is image or input. out is output. out can be:
      bool: text(T/F), str: has-text(o/x/?), ndarray: mask
    
    if inp is image and crop_h/w are None, use whole size.
    
    attrs are additional attribute added to ret dict.
    '''
    
@relation.register
def img_only_has_text(path: lambda p: (type(p) is str or
                                       isinstance(p, Path)),
                      has_text: lambda s: s in ('o', 'x', '?'),
                      crop_h=None, crop_w=None, **attrs):
    ''' Note: has_text is not 'out' in result dict. '''
    #assert iu.assert_img_path(path)
    assert Path(path).exists()
    img_h, img_w = iu.img_hw(path)
    return crop_relation(
        path, None, img_h, img_w, crop_h, crop_w,
        core.crops.yxs(img_h, img_w, crop_h, crop_w),
        has_text = has_text)

@relation.register
def default(inp, out, crop_h=None, crop_w=None, **attrs):
    raise NotImplementedError(
        'Register function for: \n'
        + str([inp, out, crop_h, crop_w, attrs]))
