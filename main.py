''' Constantly changing to test modules. Just ignore it. '''
import fire
import cli

#cli.data.add_raw('/run/media/kur/DATA1/all/DATA/test/CHN/001.jpg', '/run/media/kur/DATA1/all/DATA/test/raw', 'test2')
#cli.data.add_raw('/run/media/kur/DATA1/all/DATA/test/CHN', '/run/media/kur/DATA1/all/DATA/test/raw', 'test2')
#exit()
#cli.script.create_ids_dir('root', 2979164, 2); exit()
#cli.script.move_danbooru_crops('/home/kur/dev/szmc/SZMC_DATA/all/DATA/raw/danbooru2019/'); exit()
if __name__ == '__main__':
    fire.Fire(cli.interface)
'''
from pathlib import Path
dset_root = str(Path('../SZMC_DSET/image_only').resolve())
select_path = str(Path('../SZMC_DATA/').resolve())
dset_name = 'fmd'
import cli
cli.dset.crops_only(
    dset_root, dset_name,
    '/home/kur/dev/szmc/SZMC_DATA/clean_fmd_comics/DATA/image.h256w256/',
    select='/home/kur/dev/szmc/SZMC_DATA/clean_fmd_comics/RELS/old_select_rdt.yml')
'''

'''
#out_dir = str(Path('../SZMC_DSET/image_only/OUTS/fmd.img_only.h256w256.0_6123.0_1000.0_500').resolve())
#from out import flist
#flist.gen_and_save(dset_path, out_dir)
import cli
cli.data.crops_dir(
    '/home/kur/dev/szmc/SZMC_DATA/clean_fmd_comics/DATA/image',
    512, 512, exist_ok=True)
'''




'''
from dataset import img_only
dic = img_only.read(out_path, compression_type='ZLIB')
from pprint import pprint
pprint(dic)
# visual check # TODO: make it cli cmd

import tensorflow as tf
from utils import tensorflow_utils as tfu
def datum(example, h=None, w=None):
    img = example['img'];
    #return tf.cast(tfu.decode_raw(img, (h,w,3), tf.uint8), tf.float32)
    return tfu.decode_raw(img, (h,w,3), tf.uint8)

import cv2
print('wtf')
#for example in dic['train']:
#for example in dic['dev']:
for example in dic['test']:
    print('t')
    img = datum(example, dic['crop_height'], dic['crop_width'])
    print(img.shape)
    cv2.imshow('img', img.numpy()); cv2.waitKey(0)
    print('?')
'''
    
'''
import cli
cli.out.tfrecord(dset_path, out_path)

'''

'''
from pathlib import Path
iroot = str(Path('../SZMC_DATA/clean_fmd_comics/DATA/image/').resolve())
dset_root = str(Path('../SZMC_DSET/image_mask').resolve())
fmd_select = str(Path('../SZMC_DATA/clean_fmd_comics/RELS/old_select_rdt.yml').resolve())

import cli
cli.dset.image_only(dset_root, 'fmd', iroot,
                    select=fmd_select, has_text='x',
                    crop_h=256, crop_w=256)
'''
'''
#cli.dset.image_only(dset_root, iroot)
cli.data.canonical_select_file('clean_fmd_comics', fmd_select)
'''



#img_dir = '../SZMC_DATA/v0data/m101/prev_images/'
#mask_dir = '../SZMC_DATA/v0data/m101/mask1bit/'
#gen_crops.do(img_dir, 512, 512)
#gen_crops.do(mask_dir, 512, 512)
#szmc_v0.gen_crops(root, 512, 512)
#szmc_v0.save_crops(root, 256, 256)

'''
from utils import file_utils as fu, fp
from tasks import map_imgs
from pprint import pprint
src_dir = '../SZMC_DATA/snet285/DATA/clean_wk'
dst_dir = '../SZMC_DATA/snet285/DATA/clean_wk_dst'
exist_ok = True

#pairs = map_imgs.one_bit_masks(fu.descendants(src_dir), dst_dir)
#ps = fu.descendants(src_dir)+ fu.descendants('../SZMC_DATA/snet285/DATA/image')
#pairs = map_imgs.one_bit_masks(ps)
#pairs = map_imgs.mask1bit_dstpath_pairseq(src_dir, dst_dir)
pairs = map_imgs.mask1bit_dstpath_pairseq(src_dir)

import cv2
for i, p in pairs:
    print(p)
    cv2.imshow('i', i * 255); cv2.waitKey(0)
    
pairs = map_imgs.mask1bit_dstpath_pairseq(src_dir)
_, ps = fp.unzip(pairs)
print(len(ps))
'''

'''
# Read from input

import shutil
from utils import file_utils as fu

src = '../SZMC_DATA/snet285/'
dst = '../SZMC_DATA/a/tmp'

fu.copy_dirtree(src, dst);
'''

'''
import yaml
with open('../SZMC_DATA/v0data/m101/META/log.ymls') as f:
    dic = yaml.load(f)
from pprint import pprint
pprint(dic)

print(dic['RELATIONS'])
exit()

from pathlib import Path
szmc_v0.annotate_has_text(str(Path(root, 'prev_images')),
                          str(Path(root, 'mask1bit')), 256, 256)

'''

'''
m101 = '/home/kur/dev/szmc/SZMC_DATA/v0data/m101/'
school = '/home/kur/dev/szmc/SZMC_DATA/v0data/school/'

from pathlib import Path

from dataset import img_text_ox
img_text_ox.generate(
    '/home/kur/dev/szmc/SZMC_DSET/img.text_ox',
    'random_select', (7,2,1), 'text_ox.auto.h256w256.v1.yml',
    m101, school)
'''

'''
#from out import tfrecord
from dataset import img_text_ox
inp = '/home/kur/dev/szmc/SZMC_DSET/text_ox/DSET/img.has_text.h256w256.0_2463.0_703.0_354.yml'
#out = '/home/kur/dev/szmc/SZMC_DSET/text_ox/OUTS/img.has_text.h256w256.0_2463.0_703.0_354.tfrecord'
out = 'test.tfrecord'
img_text_ox.output(inp, out)

print('------ save & load to read ------')
from pprint import pprint
import tensorflow as tf
import funcy as F
import cv2

@tf.function
def decode_raw(str_tensor, shape, dtype=tf.uint8):
    #Decode str_tensor(no type) to dtype(defalut=tf.uint8).
    return tf.reshape(
        tf.io.decode_raw(str_tensor, dtype), shape)
tfrec = tf.data.TFRecordDataset(out)
dic = img_text_ox.read(tfrec)
h,w = dic['crop_height'], dic['crop_width']
pprint(F.omit(dic, ['train','dev','test']), sort_dicts=False)

for datum in dic['train'].take(10):
    print(datum['cls'].numpy(),
          '=',
          'has-txt' if datum['cls'] else 'no-txt')
    decoded = decode_raw(datum['img'], (h,w,3))
    img = decoded.numpy()
    cv2.imshow('im', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    cv2.waitKey(0)
print('----')
n = 0
for _ in dic['train']:
    n += 1
assert n == dic['num_train']
    
for datum in dic['dev'].take(10):
    print(datum['cls'].numpy(),
          '=',
          'has-txt' if datum['cls'] else 'no-txt')
    decoded = decode_raw(datum['img'], (h,w,3))
    img = decoded.numpy()
    cv2.imshow('im', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    cv2.waitKey(0)
print('----')
n = 0
for _ in dic['dev']:
    n += 1
assert n == dic['num_dev']
    
for datum in dic['test'].take(10):
    print(datum['cls'].numpy(),
          '=',
          'has-txt' if datum['cls'] else 'no-txt')
    decoded = decode_raw(datum['img'], (h,w,3))
    img = decoded.numpy()
    cv2.imshow('im', cv2.cvtColor(img, cv2.COLOR_RGB2BGR))
    cv2.waitKey(0)
print('----')
n = 0
for _ in dic['test']:
    n += 1
assert n == dic['num_test']

'''

'''
p1 = '../SZMC_DSET/text_ox/DSET/img.has_text.h256w256.0_2156.0_616.0_308.yml'
p2 = '../SZMC_DSET/text_ox/DSET/img.has_text.h256w256.0_2463.0_703.0_354.yml'
p3 = '../SZMC_DSET/text_ox/DSET/img.has_text.h256w256.0_2898.0_828.0_414.yml'

import funcy as F
import yaml
from pprint import pprint

from dataset import default

with open(p1) as f:
    dic1 = yaml.safe_load(f)
with open(p3) as f:
    dic3 = yaml.safe_load(f)
pprint(F.omit(dic1, ['TRAIN', 'DEV', 'TEST']))
pprint(F.omit(dic3, ['TRAIN', 'DEV', 'TEST']))
md = default.merge(p1, p3)
pprint(F.omit(md, ['TRAIN', 'DEV', 'TEST']), sort_dicts=False)

from dataset import img_text_ox
img_text_ox.merge('../SZMC_DSET/text_ox', p1, p3)
'''
