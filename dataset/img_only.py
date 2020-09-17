from pathlib import Path

import yaml
import funcy as F

from utils import file_utils as fu
from utils import fp
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
    def rel_dic(path):
        return core.dataset.relation(
            path, has_text, crop_h = 256, crop_w = 256)
    dic = F.update_in(dic, ['TRAIN'], fp.lmap(rel_dic))
    dic = F.update_in(dic, ['DEV'], fp.lmap(rel_dic))
    dic = F.update_in(dic, ['TEST'], fp.lmap(rel_dic))
    #from pprint import pprint
    #pprint(dic)
    return dic
    # Extract out crop h/w to cli
    # Add metadata
    # Make name = img_only + ver_str

    #core.dataset.relation('/home/kur/Downloads/GT.zip', has_text)

        #select_fn = 
    pairs = generate(img_root)
