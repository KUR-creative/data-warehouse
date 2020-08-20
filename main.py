''' Constantly changing for testing a modules. Just ignore it. '''
from tasks import gen_crops

img_dir = '../SZMC_DATA/v0data/m101/prev_images/'
mask_dir = '../SZMC_DATA/v0data/m101/mask1bit/'
gen_crops.do(img_dir, 512, 512)
#gen_crops.do(mask_dir, 512, 512)
