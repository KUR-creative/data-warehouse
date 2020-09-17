from pathlib import Path

import yaml
import funcy as F

from utils import file_utils as fu
from utils import fp
import core
import core.dataset 
import core.meta


def generate(img_root, select, has_text, crop_h, crop_w):
    select_path = Path(str(select))
    if not select_path.exists():
        raise NotImplementedError('Use random_select')

    dic = yaml.safe_load(select_path.read_text())
    def rel_dic(path):
        return core.dataset.relation(
            path, has_text, crop_h, crop_w)
    dic = F.update_in(dic, ['TRAIN'], fp.lmap(rel_dic))
    dic = F.update_in(dic, ['DEV'], fp.lmap(rel_dic))
    dic = F.update_in(dic, ['TEST'], fp.lmap(rel_dic))
    
    data_source = core.path.data_source(img_root)
    assert Path(data_source).exists()
    metadata = core.meta.data(
        [data_source], '',
        '이미지만 있는 데이터셋. has_text(o/x/?) 속성 있음',
        'cnet 학습을 위한 데이터셋')
        
    return F.merge(metadata, dic)
