import tensorflow as tf


def a_feature(dtype):
    return tf.io.FixedLenFeature([], dtype)

@tf.function
def decode_raw(str_tensor, shape, dtype=tf.uint8):
    ''' 
    Decode raw string tensor as dtype tensor. 
    Caution: dtype is not a casting type. 
             You need to know dtype of raw data.
             If incorrect dtype, it fail.
    '''
    return tf.reshape(
        tf.io.decode_raw(str_tensor, dtype), shape)

AUTOTUNE = tf.data.experimental.AUTOTUNE
