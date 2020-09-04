''' Proces json from VGG Image Annotator. '''
import os
from pathlib import Path
import sys
import socket

import json
import yaml
import funcy as F

import core; import core.name
from utils import fp, file_utils as fu, etc_utils as etc


def annotate_text_ox(data_source, crop_h, crop_w,
                     crop_dir, note_dir):
    '''
    crop_dir에 포함된 모든 이미지는 이름(stem)이 unique해야 함.
    note_dir에는 crop_dir의 이미지에 대한 anNOTEation이 있음.
    
    어노테이션은 dir의 구조와 상관 없이 이름으로 맵핑함.
    
    중요한 인자는 crop_dir과 note_dir임.
    
    args:
    다음 인자는 무시됨.
    crop_h: crop의 height.
    crop_w: crop의 width.
    
    다음 인자를 사용.
    data_source: 처리하려는 데이터 소스의 경로.(has DATA,META,RELS)
    
    crop_dir: 이미지를 포함하는 폴더, 플랫 구조가 아닐 수 있음.
    note_dir: crop_dir 이미지에 대한 어노테이션이 있는 폴더. 
              플랫 구조가 아닐 수 있으며 하나 이상의 어노테이션이
              포함될 수 있음.
    '''
    paths = fu.descendants(crop_dir)
    stems = [fu.stem(p) for p in paths]
    assert len(set(stems)) == len(stems)
    
    def has_text(note_dic):
        return not fp.is_empty(
            fp.get_in(note_dic, ['file_attributes']))
    stem2has_text = fp.go( # It assume some schema of json
        fu.descendants(note_dir),
        # Get all annotations
        fp.map(fu.read_text),
        fp.map(json.loads),
        lambda dics: fp.merge(*dics),
        # Make dic: { stem: has-text?(T/F) }
        fp.walk_keys(fu.stem), 
        fp.walk_values(has_text))

    # img_path => has-text?
    all_img_tfseq = ([path, stem2has_text.get(stem)]
                     for path, stem in zip(paths, stems))
    path_tfs = [[str(Path(path).relative_to(data_source)), tf]
                for path, tf in all_img_tfseq
                if tf is not None] # None: not yet annotated
    # look & feel check
    '''
    from utils import etc_utils as etc
    import cv2
    for ip, has_text in etc.inplace_shuffled(list(path_tfs)):
        print('has-text:', has_text)
        cv2.imshow('i', cv2.imread(ip))
        cv2.waitKey(0)
    '''
    
    # Make relation dict and relation name
    n_notes = len(path_tfs)
    h,w = core.name.h_w(crop_dir)
    rel_dic = {
    'NAME': {f'.n{n_notes}': '어노테이션된 crop의 수'},
    'DESCRIPTION': {
        'WHAT':('manga109로 생성한 crop에 대 KKR이 작업한 '
               +'텍스트 존재성(o/x) 어노테이션'),
        'WHY': '만화 이미지의 텍스트 존재성 분류 학습을 위해서 생성함',
        'KNWON_ERRORS':
            '사람이 한 것이기 때문에 부정확한 부분이 있을 수 있음'},
    'CREATION': {
        'HOST_NAME': socket.gethostname(),
        'DATA_SOURCE': data_source,
        'COMMAND': ' '.join(sys.argv),
        'GIT_HASH': etc.git_hash()
    },
    'HOW_TO_GEN': {
        f'img_path.has_text.h{h}w{w}':
        ( 'KKR이 작업한 어노테이션 json 파일들을 하나의 dict로 묶고 '
        + 'key에서 stem을 분리한다. crop_dir로부터 가져온 crop'
        + '들의 경로를 분리해둔 stem으로 매칭하고, dict의 values를 '
        + '적절히 처리하여 has_text(T/F)를 알아냈다.\n'
        + '저장된 경로는 DATA_SOURCE의 상대경로이다.')
    },
    'special_values': {
        'num_has_text': len(fp.lfilter(F.second, path_tfs)),
        'num_no_text': len(fp.lremove(F.second, path_tfs))},
    'RELATIONS': {f'img_path.has_text.h{h}w{w}': path_tfs}}

    rel_file_name = fu.name(crop_dir) + f'.n{n_notes}.yml'
    rel_parent = Path(data_source, 'RELS', 'crop_note')
    
    # Save relation
    os.makedirs(rel_parent, exist_ok=True)
    (rel_parent / rel_file_name).write_text(
        yaml.dump(rel_dic, allow_unicode=True, sort_keys=False))
