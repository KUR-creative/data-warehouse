import json
from pathlib import Path
import shutil
import subprocess as sp

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

def know_raws_file_type(conn_str):
    ''' 
    Add file type of image in raw 
    (only for image that has unknown type)
    '''
    with pg.connect(dbname=conn_str) as conn:
        rows = Q.unkown_file_type_raws(conn)
    from pprint import pprint

    # Save to DB
    types = list(tqdm(
        (fu.file_type_str(raw) for _,raw in rows),
        total=len(rows), desc='Get types'))
    
    # temporary cacheing (remove!)
    Path('raw.id_type.json').write_text(json.dumps(types))
    
    with pg.connect(dbname=conn_str) as conn:
        for (id, path), type in tqdm(zip(rows, types),
                                     total=len(rows),
                                     desc='insert'):
            Q.insert_file_type(conn, id=id, type=type)
        
def run_szmc_to_raws(conn_str,
                     mask_dir_name='mask',
                     rmtxt_dir_name='rmtxt'):
    '''
    Get random raw images that don't have corresponding 
    masks and rmtxt images. Generate masks and rmtxts.
    '''
    # Get raw paths
    print('Fetch raw paths from db...')
    with pg.connect(dbname=conn_str) as conn:
        Q.create(conn) # Ensure table exists.
        raw_paths = [row[0] for row in
                     Q.random_raws_without_mask_or_img(conn)]
    # Make dst paths
    to_mask = fu.replace1('raw', mask_dir_name) 
    to_rmtxt = fu.replace1('raw', rmtxt_dir_name) 
    idseq = (int(fu.stem(p)) for p in raw_paths)
    mask_pathseq = (to_mask(Path(p).with_suffix('.png'))
                    for p in raw_paths)
    rmtxt_pathseq = (to_rmtxt(p) for p in raw_paths)
    
    # Run dockerized szmc
    cmd =('docker run '
        + '-a stdin -a stdout -a stderr '
        + '-v /run/media/kur/DATA1/all/:/run/media/kur/DATA1/all '
        + '--runtime=nvidia --ipc=host --rm '
        + '-i szmc:cli-v0 python server.py').split()
    proc = sp.Popen(cmd, stdin=sp.PIPE, stdout=sp.PIPE)
    
    print('Generate mask & rmtxt using dockerized szmc')
    for id, raw, mask, rmtxt in tqdm(
            zip(idseq, raw_paths, mask_pathseq, rmtxt_pathseq),
            total=len(raw_paths)):
        # Create directory 
        Path(mask).parent.mkdir(parents=True, exist_ok=True)
        Path(rmtxt).parent.mkdir(parents=True, exist_ok=True)

        # Call dockerized szmc
        inp = f'{raw} {mask} {rmtxt}\n'
        proc.stdin.write(inp.encode('utf-8'))
        proc.stdin.flush()
        
        # Get ret and save metadata to DB
        ret = ''
        try:
            ret = proc.stdout.readline()
        except Exception as e:
            print(e)
            # Rerun proc
            #proc = sp.Popen(cmd, stdin=sp.PIPE, stdout=sp.PIPE)
        finally:
            if ret == b'Success!\n':
                mask_row = {'id':id, 'path':mask, 'type':'snet.v0'}
                img_row = {'id':id, 'path':rmtxt, 'type':'cnet.v0'}
                with pg.connect(dbname=conn_str) as conn:
                    Q.insert_mask(conn, **mask_row)
                    Q.insert_image(conn, **img_row)

    proc.stdin.write('exit the server\n'.encode('utf-8'))
