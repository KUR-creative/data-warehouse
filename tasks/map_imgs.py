from pathlib import Path

def one_bit_masks(src_paths, crop_dir=None, which=0):
    ''' 
    crop_dir is directory path to save generated crops.
    
    If None, crop_dir is 
    {common parent dir path of src_paths}.ch{which}
    
    ex) common dir = ../SZMC_DATA/masks, crop_dir = None, which=0
     =>   crop_dir = ../SZMC_DATA/masks.ch0
    
    return: [[path, 1bit-mask]]. 
    '''
    from pprint import pprint
    if crop_dir is None:
        parents = set(Path(p).parent for p in src_paths)
        assert len(parents) == 1, \
            'No common parents of src_paths. crop_dir=None is not allowed'
    pprint(src_paths)
