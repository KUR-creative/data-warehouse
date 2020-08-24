import cv2
import tensorflow as tf
from tensorflow.train import (Feature, Features, Example,
                              BytesList, FloatList, Int64List)
from tqdm import tqdm
import yaml

import core
import core.name


def generate(dset_path, out_path):
    # Load path -> dict.
    with open(dset_path) as f:
        dset_dic = yaml.safe_load(f)

    # dict -> tfrecord example
    crop_h, crop_w = core.name.h_w(dset_path)
    meta_dic = dict( # MENDATORY keys are UPPER CASE.
        num_train = _int64(len(dset_dic['TRAIN'])),
        num_dev = _int64(len(dset_dic['DEV'])),
        num_test = _int64(len(dset_dic['TEST'])),
        
        crop_height = _int64(crop_h),
        crop_width = _int64(crop_w),
        num_classes = _int64(2), # 0, 1
    )
    # TODO: meta should have :
    # average pixel value, dtype, data range, #image channels
    # #has-text, #no-text
    cls_info_dic = dict(
        classes = Feature(int64_list=Int64List(value=[0,1])),
        class_meanings = Feature(bytes_list=BytesList(
            value=[b'no_text', b'has_text'])),
    )

    # [(img, has_text)] -> examples
    pairs = dset_dic['TRAIN'] + dset_dic['DEV'] + dset_dic['TEST']
    len_data = len(pairs)
    img_cls_seq = (
        (cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB),
         has_text) for img_path, has_text in pairs)
    datumseq = ({'img': _bytes(img.tobytes()),
                 'cls': _int64(cls)}
                for img, cls in img_cls_seq) # R->D->T

    # Save examples -> file
    def serialize(dic):
        return Example(
            features=Features(feature=dic)).SerializeToString()
    with tf.io.TFRecordWriter(out_path) as out:
        out.write(serialize(meta_dic))
        out.write(serialize(cls_info_dic))
        for datum in tqdm(datumseq, total=len_data):
            out.write(serialize(datum))
    
def read(tfrecord: tf.data.TFRecordDataset):
    ''' Load tfrecord to dict. '''
    def meta(example):
        return tf.io.parse_single_example(
            example,
            {'num_train': tf.io.FixedLenFeature([], tf.int64),
             'num_dev': tf.io.FixedLenFeature([], tf.int64),
             'num_test':  tf.io.FixedLenFeature([], tf.int64),
             'crop_height':  tf.io.FixedLenFeature([], tf.int64),
             'crop_width':  tf.io.FixedLenFeature([], tf.int64),
             'num_classes':  tf.io.FixedLenFeature([], tf.int64),
            })
    def cls_info(num_classes, example):
        n = num_classes
        return tf.io.parse_single_example(
            example,
            {'classes': tf.io.FixedLenFeature(
                [n], tf.int64, [-1] * n),
             'class_meanings': tf.io.FixedLenFeature(
                [n], tf.string, [''] * n)})
    def img_cls(example):
        return tf.io.parse_single_example(
            example,
            {'img': tf.io.FixedLenFeature([], tf.string),
             'cls': tf.io.FixedLenFeature([], tf.int64)})
    for no, example in enumerate(tfrecord):
        if no == 0:
            datum = meta(example)
            num_train   = int(datum['num_train'].numpy())
            num_dev     = int(datum['num_dev'].numpy())
            num_test    = int(datum['num_test'].numpy())
            crop_height = int(datum['crop_height'].numpy())
            crop_width  = int(datum['crop_width'].numpy())
            num_classes = int(datum['num_classes'].numpy())
        elif no == 1:
            datum = cls_info(num_classes, example)
            classes = datum['classes'].numpy().tolist()
            class_meanings = [
                bs.decode('utf-8') for bs in
                datum['class_meanings'].numpy().tolist()]
        else:
            break
        
    train_data = (tfrecord.skip(2) # meta, cls_info
                          .take(num_train).map(img_cls))
    dev_data = (tfrecord.skip(2 + num_train)
                        .take(num_dev).map(img_cls))
    test_data = (tfrecord.skip(2 + num_train + num_dev)
                         .take(num_test).map(img_cls))

    return dict(
        train = train_data,
        dev   = dev_data,
        test  = test_data,
        
        num_train = num_train,
        num_dev   = num_dev,
        num_test  = num_test,
        
        crop_height = crop_height,
        crop_width  = crop_width,
        
        classes        = classes,
        class_meanings = class_meanings
    )

#---------------------------------------------------------------
def _bytes(value):
    '''Returns a bytes_list feature from a string/byte.'''
    if isinstance(value, type(tf.constant(0))):
        value = value.numpy() # BytesList won't unpack a string from an EagerTensor.
    return Feature(bytes_list=BytesList(value=[value]))
def _float(value):
    '''Returns a float_list feature from a float/double.'''
    return Feature(float_list=FloatList(value=[value]))
def _int64(value):
    '''Returns an int64_list feature from a bool/enum/int/uint.'''
    return Feature(int64_list=Int64List(value=[value]))
