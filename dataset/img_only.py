from pathlib import Path

import yaml
import funcy as F
import tensorflow as tf

from utils import file_utils as fu
from utils import tensorflow_utils as tfu
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
        'num_meta_example': 1, # number of metadata when reading tfrecord
        'crop_h': crop_h,
        'crop_w': crop_w,
        'padding': {'inp_mode': 'maximum'}, # pad mode for np.pad. it can be more!
        'num_classes': 0, # out is None.
        'num_train_img': num_train_img,
        'num_dev_img': num_dev_img,
        'num_test_img': num_test_img,
        'num_train_crop': num_train_crop,
        'num_dev_crop': num_dev_crop,
        'num_test_crop': num_test_crop,
        # number of tfrecord examples that represent metadata
    }

    # Make general metadata
    data_source = core.path.data_source(img_root)
    assert Path(data_source).exists()
    general_metadata = core.meta.data(
        [data_source], '',
        '이미지만 있는 데이터셋. has_text(o/x/?) 속성 있음',
        'cnet 학습을 위한 데이터셋')
    
    # No class, No information
    #class_information = {'class_information':{}}
    #class_information = {'class_information':{-1:'no-class'}}
        
    data = F.omit(dic, ['num_train', 'num_dev', 'num_test'])
    return F.merge(general_metadata, number_metadata, data)

def read(dset_path):
    ''' Load tfrecord to dict. '''
    tfrecord = tf.data.TFRecordDataset(dset_path)
    
    def metadata(example):
        return tf.io.parse_single_example(
            example,
            {'num_meta_example': tfu.a_feature(tf.int64),
             'num_train': tfu.a_feature(tf.int64),
             'num_dev': tfu.a_feature(tf.int64),
             'num_test': tfu.a_feature(tf.int64),
             'crop_height': tfu.a_feature(tf.int64),
             'crop_width': tfu.a_feature(tf.int64),
             'num_classes': tfu.a_feature(tf.int64),
             'DESCRIPTION_WHAT': tfu.a_feature(tf.string),
             'DESCRIPTION_WHY': tfu.a_feature(tf.string)})
    def img(example):
        return tf.io.parse_single_example(
            example,
            {'img': tf.io.FixedLenFeature([], tf.string)})
    
    meta = metadata(next(iter(tfrecord)))
    # Get metadata
    num_meta_example = int(meta['num_meta_example'].numpy())
    num_train   = int(meta['num_train'].numpy())
    num_dev     = int(meta['num_dev'].numpy())
    num_test    = int(meta['num_test'].numpy())
    crop_height = int(meta['crop_height'].numpy())
    crop_width  = int(meta['crop_width'].numpy())
    num_classes = int(meta['num_classes'].numpy())
    
    # If num_meta_example > 1, 
    # ... here some code for getting more metadata ...
    '''
    train_data = (tfrecord.skip(2) # meta, cls_info
                          .take(num_train).map(img))
    dev_data = (tfrecord.skip(2 + num_train)
                        .take(num_dev).map(img))
    test_data = (tfrecord.skip(2 + num_train + num_dev)
                         .take(num_test).map(img))
    '''

    return dict(
        #train = train_data,
        #dev   = dev_data,
        #test  = test_data,
        
        num_train = num_train,
        num_dev   = num_dev,
        num_test  = num_test,
        
        crop_height = crop_height,
        crop_width  = crop_width,
        
        #classes        = classes,
        #class_meanings = class_meanings
    )
