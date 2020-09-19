from pathlib import Path

#---------------------------------------------------------------
def parentseq(path):
    path = Path(path)
    while path not in [Path('.'), Path('/')]:
        yield path
        path = path.parent

#---------------------------------------------------------------
def flat_root_pred(root_path, *dir_names):
    if root_path is None:
        return False
    for name in dir_names:
        path = Path(root_path, name)
        if not path.exists():
            return False
    
def is_data_source(path):
    return flat_root_pred(path, 'DATA', 'META', 'RELS')

def data_source(path):
    ''' Get data-source of path. It could be path itself. '''
    for parent in parentseq(path):
        if is_data_source(parent):
            return str(parent)
    #return None
    
#---------------------------------------------------------------
def is_dataset_root(path):
    return flat_root_pred(path, 'DSET', 'META', 'OUTS')

def dataset_root(path):
    ''' Get dataset-root of path. It could be path itself. '''
    for parent in parentseq(path):
        if is_dataset_root(parent):
            return str(parent)

'''
from pprint import pprint
dset_path = str(Path('noexists'))
x = dataset_root(dset_path)
print(x, type(x))
img_dir = '../../SZMC_DATA/v0data/m101/prev_images/'
pprint(data_source(img_dir))
'''
