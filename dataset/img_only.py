from pathlib import Path

from utils import file_utils as fu


def generate(img_root):
    img_paths = fu.descendants(img_root)
    return [[p, None] for p in img_paths]

def gen_and_save(img_root, select):
    if Path(select).exists():
        pass 
        #select_fn = 
    pairs = generate(img_root)
