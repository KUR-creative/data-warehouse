from pathlib import Path
import re

from parse import parse
import yaml
import funcy as F 
from collections import namedtuple as NT

from utils import fp
from utils import etc_utils as etc
from core.split_rdt import rdt_nums, rdt_partition
import core


def generate(dst_dset_dir,
             select, RDT_ratio,
             rel_file_name, *data_sources):
    ''' 
    Generate dataset from data_sources. 
    And then save the dataset to dst_dset_dir/DSET/.
    
    dst_dset_dir is directory path to save generated dataset.
    (dst_dat_dir has DSET, META, OUTS)
    select_fn is function name defined in SELECT_FN.keys().
    RDT_ratio is (tRain ratio, Dev ratio, Test ratio).
    '''
    global SELECT_FN
    # Validate args.
    select_fn = SELECT_FN[select]
    
    for data_source in data_sources:
        assert Path(data_source).is_absolute(), \
            f'{data_source} is not absolute path.'
        
    yml_paths = [Path(data_src, 'RELS', rel_file_name)
                 for data_src in data_sources]
    for yml_path in yml_paths:
        assert yml_path.exists(), \
            f'{yml_path} is not existing path.'
        
    # Get crop size (h,w) to make 'relation name'.
    h,w = core.name.h_w(rel_file_name)
    rel_name = f'img_path.has_text.h{h}w{w}'

    # Make dataset yml path.
    dset_yml_incomplete = Path(
        dst_dset_dir, 'DSET', f'img.has_text.h{h}w{w}')
    _generate(dset_yml_incomplete, select_fn,
              RDT_ratio, rel_name,
              **F.zipdict(data_sources,
                          (yaml.safe_load(p.read_text())
                           for p in yml_paths)))
#---------------------------------------------------------------
    

def random_select(RDT_ratio, **src_rels):
    ''' 
    src_rels: {data_source: [[path, has-text?]]}
    To provide some info, it takes data_sorces as keys 
    But commonly not so useful(Because paths in rels are abs)
    
    (path, has_text)pairs, (path, no_text)pairs
    '''
    path_has_text_pairs, path_no_text_pairs = fp.go(
        fp.merge(src_rels).values(),
        fp.lcat,
        etc.inplace_shuffled,
        fp.group_by(fp.tup(lambda path, has_text: has_text)),
        lambda grouped: (grouped[True], grouped[False]))
    
    def split_rdt(pairs):
        num_rdt_tup = rdt_nums(*RDT_ratio, len(pairs))
        train,dev,test = rdt_partition(*num_rdt_tup, pairs)
        return NT('RDT', 'r d t')(train, dev, test)
    has_text = split_rdt(path_has_text_pairs)
    no_text = split_rdt(path_no_text_pairs)
    
    return dict(
        TRAIN = etc.inplace_shuffled(has_text.r + no_text.r),
        DEV = etc.inplace_shuffled(has_text.d + no_text.d), 
        TEST = etc.inplace_shuffled(has_text.t + no_text.t)) 

SELECT_FN = dict(
    random_select = random_select,
)

@F.autocurry
def make_abspath(data_source, relation): # TODO: Need tests
    ''' 
    data_source is path of directory that contains DATA dir. 
    relation is an item of some relations in rel_dic. 
    known relations: [str], [[str, bool]], [[str, path]]
    '''
    def abspath(path):
        return str(path if Path(path).is_absolute()
                   else Path(data_source, path))

    dtype = type(relation)
    if dtype is str: # [path], img only dataset
        return abspath(relation)
    elif ((dtype is list or dtype is tuple)
             and len(relation) == 2):
        a, b = relation
        return dtype([abspath(a) if type(a) is str else a,
                      abspath(b) if type(b) is str else b])
    else:
        return relation
    
# Can be refactored later..
def _generate(dset_yml_incomplete,
              select_fn, RDT_ratio,
              rel_name, **src_rel):
    ''' 
    dset_yml_incomplete is incomplete yml path to write dset.
    complete it: 'dset_yml_incomplete.revision_size.r_s.r_s.yml'
    src_rel: {data_source: relation_dict, ...} 
    rel_name: a key in RELATION in relation.yml.
    '''
    data_srcs, rel_dics = fp.unzip(src_rel.items())
    rels_list = [F.get_in(rel_dic, ['RELATIONS', rel_name])
                 for rel_dic in rel_dics]
    assert all(rels_list), 'Some rel_dic have no {rel_name} key'
    
    # Make absolute paths
    rels_list = [fp.lmap(make_abspath(dat_src), rels)
                 for dat_src, rels in zip(data_srcs, rels_list)]
    
    # Select R/D/T
    rdt_dic = select_fn(RDT_ratio,
                        **F.zipdict(data_srcs, rels_list))
    
    # Make out dict.
    data_sources = list(src_rel.keys())
    meta_dic = {
    'NAME': {
        'img_path.has_text': '[[이미지 경로, 텍스트 존재성]] 관계 모음',
        'h{h}w{w}': 'crop 크기'},
    'DATA_SOURCES': data_sources,
    'DESCRIPTION': {
        'WHAT': 'DATA_SOURCES에 존재하는 이미지:텍스트 존재성 관계를 모아 R/D/T로 생성한 데이터셋',
        'WHY': '만화 이미지의 텍스트 존재성 분류 학습을 위해서 생성함',
        'KNWON_ERRORS': None},
    'HOW_TO_GEN': 'cli cmd...'}
    out_dic = F.merge(meta_dic, rdt_dic)
    
    # Make yaml file path.
    r_train = 0; r_dev = 0; r_test = 0; # r: revision
    n_train = len(rdt_dic['TRAIN']) # n: num (size)
    n_dev = len(rdt_dic['DEV'])
    n_test = len(rdt_dic['TEST'])
    ver_str =(f'.{r_train}_{n_train}'
            + f'.{r_dev}_{n_dev}'
            + f'.{r_test}_{n_test}.yml')
    dset_file_path = Path(str(dset_yml_incomplete) + ver_str)

    # Save dataset to file.
    dset_file_path.write_text(
        yaml.dump(out_dic, allow_unicode=True, sort_keys=False))
