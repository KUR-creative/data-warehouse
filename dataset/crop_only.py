from pathlib import Path

import yaml
from tqdm import tqdm

from utils import fp
from utils import file_utils as fu
from utils import image_utils as iu

import core
import core.meta
import core.path

def generate(crops_root, select):
    select_path = Path(str(select))
    if not select_path.exists():
        raise NotImplementedError('Use random_select')
    
    dic = yaml.safe_load(select_path.read_text())
    ids = {'TRAIN':set(int(fu.stem(p)) for p in dic['TRAIN']),
           'DEV':  set(int(fu.stem(p)) for p in dic['DEV']),
           'TEST': set(int(fu.stem(p)) for p in dic['TEST'])}
    def group(id):
        return('TEST' if id in ids['TEST']
          else 'DEV' if id in ids['DEV']
          else 'TRAIN' if id in ids['TRAIN']
          else None)
    
    crop_paths = fu.descendants(crops_root)
    crop_path_dic = fp.group_by(
        lambda p: group(int(fu.stem(p).split('_')[0])),
        fu.descendants(crops_root))

    crop_h, crop_w = iu.img_hw(crop_path_dic['TEST'][0])
    for h,w in tqdm((iu.img_hw(p) for p in crop_paths),
                    desc='Checking crop size integrity',
                    total=len(crop_paths)):
        assert crop_h == h and crop_w == w
    number_metadata = {
        'crop_h': crop_h,
        'crop_w': crop_w,
        'num_train_img': len(dic['TRAIN']),
        'num_dev_img': len(dic['DEV']),
        'num_test_img': len(dic['TEST']),
        'num_train_crop': len(crop_path_dic['TRAIN']),
        'num_dev_crop': len(crop_path_dic['DEV']),
        'num_test_crop': len(crop_path_dic['TEST'])
    }
    
    data_source = core.path.data_source(crops_root)
    assert Path(data_source).exists()
    general_metadata = core.meta.data(
        [data_source], '',
        '이미지만 있는 데이터셋. 이미 crop되어 있음',
        '남의 cnet 전이 학습을 위한 crop 데이터셋')

    return fp.merge(
        general_metadata, number_metadata, crop_path_dic)

