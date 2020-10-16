import shutil
from pathlib import Path
import json

from utils import file_utils as fu


def main(db2019dir, dstpath=None):
    ''' Move useless image crop files in db2019dir to dstpath. '''
    from pprint import pprint
    # Directory paths
    src = Path(db2019dir)
    if dstpath is None:
        dstpath = fu.replace1('raw', 'old', src)
    dst = Path(dstpath)
    assert src.exists()
    assert dst.parent.exists() # assert old dir exists
    
    # Make source -> destination crop paths
    crop_paths = [p for p in fu.descendants(src)
                  if '_' in fu.stem(p)]
    dst_paths = [str(dst / Path(p).relative_to(src))
                 for p in crop_paths]

    # Create directory and Move crops: side-effects
    fu.copy_dirtree(src, dst)
    for src_path, dst_path in zip(crop_paths, dst_paths):
        shutil.move(src_path, dst_path)
        print(src_path, '->', dst_path)

    # Save move history in a file
    history = [{'src': src, 'dst': dst}
               for src, dst in zip(crop_paths, dst_paths)]
    Path('moved.danbooru2019.crops.json').write_text(
        json.dumps(history, indent=2))
