from pathlib import Path

import core
import core.io
from utils import file_utils as fu
from utils import fp 


def canonical_select(data_source, select_fpath, out_path):
    ''' 
    Only accept the "old valid flist file" as select_fpath. 
    This functions is just script. Not a general one.
    '''
    assert 'valid' in select_fpath, 'only valid one'
    with open(select_fpath) as f:
        dev_relpaths = fp.go(
            f.readlines(),
            fp.filter(lambda line: 'danbooru_raw' not in line),
            fp.lmap(lambda s:
                Path(s.strip()).relative_to('clean_fmd_comics')))
    img_root = Path(data_source, 'DATA', 'image')
    all_paths = fu.descendants(img_root)
    dev_test_paths = [str(img_root / p) for p in dev_relpaths]
    split_len = len(dev_test_paths) // 3 * 2 # dev:test = 2:1
    # R/D/T
    train_paths = list(set(all_paths) - set(dev_test_paths))
    dev_paths = dev_test_paths[:split_len]
    test_paths = dev_test_paths[split_len:]
    # Generate R/D/T selection data . TRAIN, DEV, TEST are mandatory
    rdt_dic = dict(num_train = len(train_paths),
                   num_dev = len(dev_paths),
                   num_test = len(test_paths),
                   TRAIN = fp.lmap(str, train_paths),
                   DEV = fp.lmap(str, dev_paths),
                   TEST = fp.lmap(str, test_paths))
    # Save select-yml file
    if out_path == None:
        RELS_path = Path(select_fpath).parent
        out_path = RELS_path / 'old_select_rdt.yml'
    core.io.dump_data_yaml(out_path, rdt_dic)
