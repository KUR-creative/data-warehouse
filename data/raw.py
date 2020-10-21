import json
from pathlib import Path
import shutil

import aiosql
import filetype
import funcy as F
import psycopg2 as pg
from tqdm import tqdm

import core
from utils import fp
from utils import file_utils as fu
from utils import image_utils as iu


Q = aiosql.from_path('./data/raw.sql', 'psycopg2')
def max_id(conn):
    ret = Q.max_id(conn)
    return ret if ret is not None else -1 #For +1 to next-id

def ready_to_add(src_path, raw_dir, conn_str, n_digits):
    assert Path(src_path).exists()
    
    dp = Path(raw_dir)
    if not dp.exists() or fp.is_empty(fu.children(dp)):
        dp.mkdir(parents=True, exist_ok=True)
        for dir in core.path.id_dirs(dp, n_digits):
            Path(dir).mkdir(parents=True)
            
def add(src_path, dst_dir, conn_str):
    '''
    Add src images to dst. Rename img in id. 
    ids saved in dst_dir/000~999/xxx000.ext
    Temporary code. Need refactor and remove cacheings
    
    src_path can be direcotry path or file that contaions
    image paths line by line.
    dst_dir is directory path.
    conn_str for db connection
    '''
    # Get paths of files to move
    src_path = Path(src_path)
    src_paths =(fu.descendants(src_path) if src_path.is_dir()
                else src_path.read_text().splitlines())
    print('src_paths created')
    
    # Mapping file path -> file type
    data_source = Path(core.path.data_source(src_path))
    path2type_cache = data_source/'RELS'/'raw.path2type.json'
    if path2type_cache.exists():
        path2type = json.loads(path2type_cache.read_text())
        print('path2type loaded from cache:', str(path2type_cache))
    else:
        path2type = F.zipdict(
            src_paths, tqdm(map(fu.file_type_str, src_paths),
                            total=len(src_paths), desc='FileType'))
        try:
            Path('tmp.cache.json').write_text(json.dumps(path2type))
        except Exception as e:
            print(e)
        print('path2type created')
    
    # Group images and others
    def is_img_path(path):
        return path2type[path].split('/')[0] == 'image'
    grouped = fp.group_by(is_img_path, src_paths)
    img_paths, other_paths = grouped[True], grouped[False] 
    print('img / others gropued')

    # Make new dst paths
    n_digits = len(Path(fu.children(dst_dir)[0]).stem)
    def id_dir(n_digits, id):
        return f'%0{n_digits}d' % (id % 10**n_digits)
    def raw_path(root, n_digits, id, ext):
        return Path(root, id_dir(n_digits, id), f'{id}.{ext}')
    
    with pg.connect(dbname=conn_str) as conn:
        Q.create(conn) # Ensure table exists.
        now_id = max_id(conn) + 1
    ids = range(now_id, now_id + len(img_paths))
    img_extensions = (fu.extension(p) for p in img_paths)
    file_typeseq = (path2type[p] for p in img_paths)
    raw_pathseq = (raw_path(dst_dir, n_digits, id, ext)
                   for id, ext in zip(ids, img_extensions))
    #assert len(raw_paths) == len(img_paths), f'{len(raw_paths)} != {len(img_paths)}'
    #print('destination paths created')
    
    # Save to DB. Side-effect!
    rows_cache = data_source/'RELS'/'raw.rows.json'
    if rows_cache.exists():
        rows = json.loads(rows_cache.read_text())
        print('rows loaded from cache:', rows_cache)
    else:
        rows = list(tqdm(
            ({'id': id,
              'src': str(Path(src).resolve()),
              'raw': str(Path(raw).resolve())}
             for id, src, raw in zip(ids, img_paths, raw_pathseq)),
            total=len(img_paths)))
        rows_cache.write_text(json.dumps(rows))
        print('rows created')
    with pg.connect(dbname=conn_str) as conn:
        '''
        Q.insert_id_path_rows(conn, rows)
        Q.insert_no_care_files(
            conn, [{'path':p} for p in other_paths])
        Q.insert_file_types(
            conn, [{'id':id, 'type':type}
                    for id, type in zip(ids, file_typeseq)])
        '''
        zipped = tqdm(
            zip(rows, ({'id':d['id'], 'type':type}
                       for d, type in zip(rows, file_typeseq))),
            total=len(rows), desc='Save to DB')
        for id_path, file_type in zipped:
            Q.insert_id_path_row(conn, **id_path)
            Q.insert_file_type(conn, **file_type)
        for no_care_file in ({'path':p} for p in other_paths):
            Q.insert_no_care_file(conn, **no_care_file)
    print('All data saved to db')
    
    #exit()
    # Move files
    with pg.connect(dbname=conn_str) as conn:
        src_dst_pairs = Q.src_raw(conn)
    n_moved = 0
    for src, dst in tqdm(src_dst_pairs, desc='Move'):
        if Path(src).exists():
            #shutil.copy(src, dst)
            #print(src, '->', dst)
            shutil.move(src, dst)
            n_moved += 1
    print(f'{n_moved} images have been moved.')
    if n_moved == 0 or n_moved == len(rows):
        print('May be all images moved')

def relocate(conn_str):
    ''' move images from 'raw' to 'src' described in db '''
