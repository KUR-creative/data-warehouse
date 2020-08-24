''' Constantly changing for testing a modules. Just ignore it. '''

#img_dir = '../SZMC_DATA/v0data/m101/prev_images/'
#mask_dir = '../SZMC_DATA/v0data/m101/mask1bit/'
#gen_crops.do(img_dir, 512, 512)
#gen_crops.do(mask_dir, 512, 512)
root = '../SZMC_DATA/v0data/m101/DATA'
#szmc_v0.gen_crops(root, 512, 512)
#szmc_v0.save_crops(root, 256, 256)


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

import fire
import cli
if __name__ == '__main__':
    fire.Fire(cli.interface)
