import tensorflow as tf

def a_feature(dtype):
    return tf.io.FixedLenFeature([], dtype)
