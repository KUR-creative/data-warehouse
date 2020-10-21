from pathlib import Path

from utils import file_utils as fu

#---------------------------------------------------------------
def parentseq(path):
    path = Path(path)
    while path not in [Path('.'), Path('/')]:
        yield path
        path = path.parent

#---------------------------------------------------------------
def is_data_source(path):
    return(path is not None and
           Path(path, 'DATA').exists() and
           Path(path, 'META').exists() and
           Path(path, 'RELS').exists())

def data_source(path):
    ''' Get data-source of path. It could be path itself. '''
    for parent in parentseq(path):
        if is_data_source(parent):
            return str(parent)
    #return None
    
#---------------------------------------------------------------
def is_dataset_root(path):
    return(path is not None and
           Path(path, 'DSET').exists() and
           Path(path, 'META').exists() and
           Path(path, 'OUTS').exists())

def dataset_root(path):
    ''' Get dataset-root of path. It could be path itself. '''
    for parent in parentseq(path):
        if is_dataset_root(parent):
            return str(parent)

'''
from pprint import pprint
dset_path = str(Path('../SZMC_DSET/image_only/DSET/fmd.img_only.h256w256.0_6123.0_1000.0_500.yml').resolve())
pprint(dataset_root(dset_path))
img_dir = '../../SZMC_DATA/v0data/m101/prev_images/'
pprint(data_source(img_dir))
'''

def crop(img_path, y, x, fmt='_y{y}x{x}'):
    new_stem = fu.stem(img_path) + fmt.format(y=y, x=x)
    return fu.set_stem(img_path, new_stem)

def id_dirs(parent, n_digits=3):
    return [str(Path(root, f'%0{n_digits}d' % i))
            for i in range(0, 10**n_digits)]
