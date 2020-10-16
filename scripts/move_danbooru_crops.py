from pathlib import Path
from utils import file_utils as fu


def main(db2019dir, dst_path=None):
    src = Path(db2019dir)
    from pprint import pprint
    #pprint(fu.children(src))
    print(src)
    print(src.resolve())
    crop_paths = fu.descendants(src)
