from pathlib import Path


def is_data_source(path):
    return(Path(path, 'DATA').exists() and
           Path(path, 'META').exists() and
           Path(path, 'RELS').exists())

def data_source(path):
    ''' Get data-dource of path. It could be path itself. '''
    def parents(path):
        path = Path(path)
        while path != Path('.'):
            yield path
            path = path.parent
            
    for parent in parents(path):
        if is_data_source(parent):
            return str(parent)
    #return None

'''
from pprint import pprint
img_dir = '../../SZMC_DATA/v0data/m101/prev_images/'
pprint(data_source(img_dir))
'''
