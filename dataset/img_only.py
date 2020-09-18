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
    
    # Make path to relation
    def rel_dic(path):
        return core.dataset.relation(
            path, has_text, crop_h, crop_w)
    dic = F.update_in(dic, ['TRAIN'], fp.lmap(rel_dic))
    dic = F.update_in(dic, ['DEV'], fp.lmap(rel_dic))
    dic = F.update_in(dic, ['TEST'], fp.lmap(rel_dic))
    
    # number of data relation and image
    num_train_img = dic['num_train']
    num_dev_img = dic['num_dev']
    num_test_img = dic['num_test']
    num_train_crop = sum(len(d['yxs']) for d in dic['TRAIN'])
    num_dev_crop = sum(len(d['yxs']) for d in dic['DEV'])
    num_test_crop = sum(len(d['yxs']) for d in dic['TEST'])
    
    # Make num_xx to num_xx_img, Add num_xx_crop
    number_metadata = {
        'crop_h': crop_h,
        'crop_w': crop_w,
        'num_train_img': num_train_img,
        'num_dev_img': num_dev_img,
        'num_test_img': num_test_img,
        'num_train_crop': num_train_crop,
        'num_dev_crop': num_dev_crop,
        'num_test_crop': num_test_crop
    }
    
    # Make general metadata
    data_source = core.path.data_source(img_root)
    assert Path(data_source).exists()
    general_metadata = core.meta.data(
        [data_source], '',
        '이미지만 있는 데이터셋. has_text(o/x/?) 속성 있음',
        'cnet 학습을 위한 데이터셋')
        
    dic = F.omit(dic, ['num_train', 'num_dev', 'num_test'])
    return F.merge(general_metadata, number_metadata, dic)
