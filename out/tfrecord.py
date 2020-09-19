import numpy as np
import tensorflow as tf
from tensorflow.train import (Feature, Features, Example,
                              BytesList, FloatList, Int64List)
from tqdm import tqdm
import yaml

from utils import image_utils as iu
from utils import fp 

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

def serialize(dic):
    return Example(
        features=Features(feature=dic)).SerializeToString()

#---------------------------------------------------------------
def gen_and_save(dset_path, out_path): # TODO: extract and relocate reusable logic to out.tfrecord
    # Load path -> dict.
    with open(dset_path) as f:
        dset = yaml.safe_load(f)

    # Make metadata
    meta_dic = dict(
        num_meta_example = _int64(dset['num_meta_example']),
        # NOTE: num_xx_crop are derived value. You can just use sum of len of R/D/T crops.
        # Each crops(yxs) of img is also derived, you can calc them.
        num_train = _int64(dset['num_train_crop']),
        num_dev = _int64(dset['num_dev_crop']),
        num_test = _int64(dset['num_train_crop']),
        crop_height = _int64(dset['crop_h']),
        crop_width = _int64(dset['crop_w']),
        num_classes = _int64(dset['num_classes']),
        DESCRIPTION_WHAT = _bytes(str.encode(
            dset['DESCRIPTION']['WHAT'])),
        DESCRIPTION_WHY = _bytes(str.encode(
            dset['DESCRIPTION']['WHY'])),
    )

    # Make classes information
    #classes = [-1]
    '''
    classes = list(dset['class_information'].keys())
    class_meanings = list(dset['class_information'].values())
    cls_info_dic = dict(
        classes = Feature(int64_list=Int64List(value=classes)),
        class_meanings = Feature(bytes_list=BytesList(
            value=[str.encode(s) for s in class_meanings])),
    )
    '''
    # yxs (o), crop_h/w (o), img only
    def pad(img, crop_h, crop_w, mode):
        ih = img.shape[0]; iw = img.shape[1]
        padding = [
            (0, crop_h - ih), (0, crop_w - iw)
        ] + [(0, 0)] if len(img.shape) == 3 else [] # for (h,w) img
        return np.pad(img, padding, mode=mode)
    def inp_cropseq(rel_dic, crop_h, crop_w, pad_mode):
        ''' rel_dic is an elem of dset[TRAIN|DEV|TEST] '''
        yxs = rel_dic['yxs']
        img = iu.cv.read_rgb(rel_dic['inp'])
        cropseq = (img[y:y+crop_h, x:x+crop_w] for y,x in yxs)
        return (pad(crop, crop_h, crop_w, pad_mode)
                for crop in cropseq)
    def datumseq(rel_dic, dset):
        h = dset['crop_h']
        w = dset['crop_w']
        mode = dset['padding']['inp_mode']
        return ({'img': _bytes(img.tobytes())}
                for img in inp_cropseq(rel_dic, h, w, mode))
    all_datumseq = fp.mapcat(
        lambda rel: datumseq(rel, dset),
        dset['TRAIN'] + dset['DEV'] + dset['TEST'])
    
    '''
    import cv2
    for datum in all_datumseq:
        cv2.imshow('img', datum['img']); cv2.waitKey(0)
    '''
        

    # Make data sequence(crop y/n)
    
    # Padding method: (text-o/x = mirror)
                    # (snet = white for image, black for mask)
                    # (cnet = white for image)
    #datumseq = (
    with tf.io.TFRecordWriter(out_path, 'ZLIB') as out:
        out.write(serialize(meta_dic))
        #out.write(serialize(cls_info_dic))
        num_crops = sum([
            dset[k] for k in
            ('num_train_crop', 'num_dev_crop', 'num_test_crop')
        ])
        for datum in tqdm(all_datumseq, total=num_crops):
            out.write(serialize(datum))
    
#def read(tfrecord: tf.data.TFRecordDataset):
