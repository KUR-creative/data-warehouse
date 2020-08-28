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
