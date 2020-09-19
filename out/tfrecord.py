import yaml
import tensorflow as tf
from tensorflow.train import (Feature, Features, Example,
                              BytesList, FloatList, Int64List)

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
        dset_dic = yaml.safe_load(f)

    # Make metadata
    crop_h = dset_dic['crop_h']
    crop_w = dset_dic['crop_w']
    meta_dic = dict(
        num_meta_example = _int64(dset_dic['num_meta_example']),
        # NOTE: num_xx_crop are derived value. You can just use sum of len of R/D/T crops.
        # Each crops(yxs) of img is also derived, you can calc them.
        num_train = _int64(dset_dic['num_train_crop']),
        num_dev = _int64(dset_dic['num_dev_crop']),
        num_test = _int64(dset_dic['num_train_crop']),
        crop_height = _int64(crop_h),
        crop_width = _int64(crop_w),
        num_classes = _int64(dset_dic['num_classes']),
        DESCRIPTION_WHAT = _bytes(str.encode(
            dset_dic['DESCRIPTION']['WHAT'])),
        DESCRIPTION_WHY = _bytes(str.encode(
            dset_dic['DESCRIPTION']['WHY'])),
    )

    # Make classes information
    #classes = [-1]
    '''
    classes = list(dset_dic['class_information'].keys())
    class_meanings = list(dset_dic['class_information'].values())
    cls_info_dic = dict(
        classes = Feature(int64_list=Int64List(value=classes)),
        class_meanings = Feature(bytes_list=BytesList(
            value=[str.encode(s) for s in class_meanings])),
    )
    cls_info_dic = dict(
        classes = Feature(int64_list=Int64List(value=[0,1])),
        class_meanings = Feature(bytes_list=BytesList(
            value=[b'no_text', b'has_text'])),
    )
    '''

    #print(meta_dic)
    #print(cls_info_dic)
    
    # Make data sequence(crop y/n)
    # Padding method: (text-o/x = mirror)
                    # (snet = white for image, black for mask)
                    # (cnet = white for image)
    #datumseq = (
    with tf.io.TFRecordWriter(out_path) as out:
        out.write(serialize(meta_dic))
        #out.write(serialize(cls_info_dic))
        #for datum in tqdm(datumseq, total=len_data):
            #out.write(serialize(datum))
    
#def read(tfrecord: tf.data.TFRecordDataset):
