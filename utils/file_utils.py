'''
Utils for File Processing
'''
import os
from pathlib import PurePosixPath, Path
import re
import shutil

import chardet
import funcy as F

#---------------------------------------------------------------
def children(dirpath):
    ''' Return children file path list of `dirpath` '''
    parent = Path(dirpath)
    return list(map(
        lambda child_path: str(parent / child_path.name),
        parent.iterdir()
    ))

def descendants(root_dirpath):
    ''' Return descendants file path list of `root_dirpath` ''' 
    fpaths = []
    it = os.walk(root_dirpath)
    for root,dirs,files in it:
        for path in map(lambda name:PurePosixPath(root) / name,files):
            fpaths.append(str(path))
    return fpaths

#---------------------------------------------------------------
def copy_dirtree(src, dst, **kwargs):
    ''' 
    Copy all directories under src dir path, except files.
    If dst is not exists, it creates directory path.
    (if a/b/c/, then all of directories created!)
    
    See help(shutil.copytree) for kwargs if you want.
    '''
    def ignore(dir, files):
        return [f for f in files if Path(dir, f).is_file()]
    shutil.copytree(src, dst, ignore=ignore, **kwargs)

def copy_path_pairs(src_root, dst_root):
    '''
    Generate [[src-path dst-path]]. 
    [src-path] is descendants of src_root.
     ex) src_root/a/b src_root/a/c src_root/a src_root/a/bc/d
    [dst-path] is src-path with root replaced by dst_root.
     ex) dst_root/a/b dst_root/a/c dst_root/a dst_root/a/bc/d

    Note: Before copying files using return list from this func, 
    call copy_dirtree first to ensure each directory exists.
    
    args: str or Path like object
    return: [[src-path dst-path]]. All atom is str.
    '''
    src_root = Path(src_root)
    dst_root = Path(dst_root)
    src_paths = [Path(p) for p in descendants(src_root)]
    rel_paths = [p.relative_to(src_root) for p in src_paths]
    dst_paths = [dst_root / p for p in rel_paths]
    return [[str(src), str(dst)]
            for src, dst in zip(src_paths, dst_paths)]

#pairs = copy_path_pairs('.', './tmp/asdf')# special case? # paths have no root(not presented)..
#pairs = copy_path_pairs('../__pycache__', 'bbap')
#pairs = copy_path_pairs('/boot/grub', './tmp')
#pairs = copy_path_pairs('./__pycache__/', 'a/b/c/d/e')
#pairs = copy_path_pairs('noexists', './tmp') # no paths case
#from pprint import pprint
#pprint(pairs)

#---------------------------------------------------------------
@F.autocurry
def replace1(old, new, path):
    parts = list(Path(path).parts) # NOTE: because of set_in implementation..
    idx = parts.index(old)
    return str(Path(*F.set_in(parts, [idx], new)))

def select(at, path=None):
    ''' Select part of path '''
    if path is None:
        return lambda path: select(at, path)
    else:
        parts = Path(path).parts
        assert -len(parts) <= at < len(parts)
        return parts[at]

def extension(path):
    return Path(path).suffix.replace('.','',1)

def stem(path): return Path(path).stem
def name(path): return Path(path).name
    
def set_stem(path, stem: str):
    return str(Path(path).parent / (stem + Path(path).suffix))

def path_str(path):
    ''' 
    Remove small useless things in path string.
    ex) ./foo/bar/ -> foo/bar 
    DO NOT directly cast Path to str, Call it instead.
    '''
    return str(Path(path))

#---------------------------------------------------------------
def human_sorted(iterable):
    ''' Sorts the given iterable in the way that is expected. '''
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    return sorted(iterable, key = alphanum_key)

#---------------------------------------------------------------
def write_text(path, text, mode=0o777, exist_ok=True):
    path = Path(PurePosixPath(path))
    os.makedirs(path.parent, mode, exist_ok)
    path.write_text(text)

def read_text(path, encoding=None, errors=None):
    ''' If encoding = 'AUTO', then detect encoding. '''
    if encoding == 'AUTO':
        with open(path, 'rb') as f:
            rawdata = f.read()
            encoding = chardet.detect(rawdata)['encoding']
        #print('path->',path)
    return Path(path).read_text(
        encoding=encoding, errors=errors)
