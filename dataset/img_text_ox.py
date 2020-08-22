from pathlib import Path
import re

from parse import parse
import yaml
import funcy as F 

from utils import fp


def generate(select, RDT, rel_file_name, *data_sources):
    ''' RDT is (tRain ratio, Dev ratio, Test ratio) '''
    global SELECT_FN
    # Validate args
    select_fn = SELECT_FN[select]
    
    for data_source in data_sources:
        assert Path(data_source).is_absolute(), \
            f'{data_source} is not absolute path.'
        
    yml_paths = [Path(data_src, 'RELS', rel_file_name)
                 for data_src in data_sources]
    for yml_path in yml_paths:
        assert yml_path.exists(), \
            f'{yml_path} is not existing path.'
        
    # Get crop size (h,w) to make 'relation name'
    crop_size_strs = re.findall('h[1-9]+w[1-9]+', rel_file_name)
    assert len(crop_size_strs) == 1, f'{len(crop_size_strs)} != 1'
    hw_str = crop_size_strs[0]
    h,w = map(int, parse('h{}w{}', hw_str))
    rel_name = f'img_path.text_ox.h{h}w{w}'
    _generate(select_fn, RDT, rel_name,
              **F.zipdict(data_sources,
                          (yaml.safe_load(p.read_text())
                           for p in yml_paths)))
#---------------------------------------------------------------
    
from pprint import pprint

def random_select(num_train, num_dev, num_test, **src_rels):
    print(num_train, num_dev, num_test)
    pprint(src_rels)

SELECT_FN = dict(
    random_select = random_select,
)

@F.autocurry
def make_abspath(data_source, relation):
    ''' 
    data_source is path of directory that contains DATA dir. 
    relation is an item of some relations in rel_dic. 
    known relations: [str], [[str, bool]], [[str, path]]
    '''
    def abspath(path):
        p = Path(path)
        return p if p.is_absolute() else Path(data_source, p)

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
    
def _generate(select_fn, RDT, rel_name, **src_rel):
    ''' src_rel: {data_source: relation_dict, ...} '''
    data_srcs, rel_dics = fp.unzip(src_rel.items())
    rels_list = [F.get_in(rel_dic, ['RELATIONS', rel_name])
                 for rel_dic in rel_dics]
    assert all(rels_list), 'Some rel_dic have no {rel_name} key'
    
    # Make absolute paths
    rels_list = [fp.lmap(make_abspath(dat_src), rels)
                 for dat_src, rels in zip(data_srcs, rels_list)]
    
    #pprint(rels_list)
    rdt_dic = select_fn(*RDT, **F.zipdict(data_srcs, rels_list))
