from pathlib import Path

import yaml

from utils import file_utils as fu
import core
import core.dataset 


def generate(img_root):
    img_paths = fu.descendants(img_root)
    return [[p, None] for p in img_paths]

# def relations
def gen_and_save(img_root, select, has_text):
    select_path = Path(str(select))
    if not select_path.exists():
        raise NotImplementedError('Use random_select')

    dic = yaml.safe_load(select_path.read_text())
    #TODO map dic with relation
    x = core.dataset.relation(dic['TEST'][0], has_text,
                              crop_h = 256, crop_w = 256)
    # Extract out crop h/w to cli
    # Add metadata
    # Make name = img_only + ver_str

    from pprint import pprint

    #core.dataset.relation('/home/kur/Downloads/GT.zip', has_text)

        #select_fn = 
    pairs = generate(img_root)
