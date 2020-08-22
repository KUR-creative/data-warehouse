import os
from pathlib import Path

import cv2
import imagesize
import yaml

from tasks import gen_crops
from utils import file_utils as fu, fp


#---------------------------------------------------------------
def generate_crops(data_source, h, w): # TODO: refactor
    # Get src images
    DATA_dir = Path(data_source, 'DATA')
    org_dir = Path(DATA_dir, 'prev_images') 
    mask_dir = Path(DATA_dir, 'mask1bit')
    _gen_crops(DATA_dir, org_dir, h, w)
    _gen_crops(DATA_dir, mask_dir, h, w)

def annotate_text_ox(data_source, h=None, w=None):
    ''' If h,w is passed, Use cropped directories. '''
    
    assert (h is None and w is None) or (h > 0 and w > 0)
    org_dir = Path(data_source, 'DATA', 'prev_images') 
    mask_dir = Path(data_source, 'DATA', 'mask1bit')

    # Get cropped paths (TODO: would be extracted as a function)
    if h is not None and w is not None:
        org_stem = org_dir.stem + f'.h{h}w{w}'
        mask_stem = mask_dir.stem + f'.h{h}w{w}'
        org_dir = org_dir.parent / 'crop' / org_stem
        mask_dir = mask_dir.parent / 'crop' / mask_stem
    assert org_dir.exists(), f'{org_dir} is not exists.'
    assert mask_dir.exists(), f'{mask_dir} is not exists.'
    
    org_paths = fu.human_sorted(fu.descendants(org_dir))
    mask_paths = fu.human_sorted(fu.descendants(mask_dir))
    assert len(org_paths) == len(mask_paths)
    
    threshold_8bit_rgb_mask = 333500
    _annotate_text_ox_img_mask_pairs(
        org_paths, mask_paths, data_source,
        threshold_8bit_rgb_mask, h, w)
    
#---------------------------------------------------------------
def _gen_crops(DATA_dir, img_dir, h, w, dst_crops_dir=None):
    '''
    DATA_dir: 데이터 소스의 DATA 디렉토리 경로
    img_dir: 자르려는 이미지가 존재하는 디렉토리의 경로
    h, w: 잘려져 나오는 crop의 크기
    dst_crops_dir: crop이 저장되는 디렉토리 경로
    '''
    # Get src images
    assert img_dir.exists()
    
    if dst_crops_dir is None:
        dst_crops_dir = Path(
            DATA_dir, 'crop', f'{img_dir.stem}.h{h}w{w}')
    
    # Generate (path, crop)s
    paths = fu.human_sorted(fu.descendants(img_dir))
    path_crop_seq = gen_crops.do(paths, h, w, dst_crops_dir)
    
    # look & feel check
    '''
    from funcy import take
    for p, c in take(40, path_crop_seq):
        print(' org:', p, c.shape);
        cv2.imshow('c',c);
        cv2.waitKey(0)
    exit()
    '''
    
    # Save to dst directories
    os.makedirs(dst_crops_dir, exist_ok=True)
    # TODO: makedirs parents.. preserve directory structure.
    
    print(f'start: _gen_crops({DATA_dir}, {img_dir}, {h}, {w}, {dst_crops_dir})')
    for path, crop in path_crop_seq:
        cv2.imwrite(path, cv2.cvtColor(crop, cv2.COLOR_RGB2BGR))
    print('finished')

def _annotate_text_ox_img_mask_pairs(
        org_paths, mask_paths, data_source, no_text_threshold,
        h=None, w=None):
    ''' 
    If h,w is passed, Use only (h,w) sized crops. 
    If mask.sum() > no_text_threshold, then mask has text.
    '''
    assert len(org_paths) == len(mask_paths)
    rels_dir = Path(data_source, 'RELS')
    assert rels_dir.exists()
    
    # Use only (h,w) sized crops.
    def is_hw_size(path):
        if h is not None and w is not None:
            img_w,img_h = imagesize.get(path)
            return img_w == w and img_h == h
        else:
            return True # Use all.
    org_crop_paths = fp.filter(is_hw_size, org_paths)
    mask_crop_paths = fp.lfilter(is_hw_size, mask_paths)
        
    # Save relative path
    org_rel_paths = (str(Path(p).relative_to(data_source))
                     for p in org_crop_paths)
    
    # Map mask_seq to has-text? (T/F)
    mask_seq = (cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB)
                for p in mask_crop_paths) # TODO: rgba?
    has_texts = [bool(m.sum() > no_text_threshold)
                 for m in mask_seq]
    img_tfs = [[p,b] for p,b in zip(org_rel_paths, has_texts)]
    
    # look & feel check
    '''
    from utils import etc_utils as etc
    for ip, has_text in etc.inplace_shuffled(list(img_tfs)):
        print('has-text:', has_text)
        cv2.imshow(
            'i', cv2.cvtColor(cv2.imread(ip), cv2.COLOR_BGR2RGB))
        cv2.waitKey(0)
    '''
    
    # Save to has_text.auto.1_{len(paths)}.yml #TODO: Refactor
    version = 1
    rel_size = len(img_tfs)
    rel_dic = {
    'NAME': {
        'text_ox': '텍스트 존재성에 관한 데이터',
        'auto': '자동으로 생성한 데이터(어노테이션)',
        #f'{version}_{rel_size}': 'version 개정 버전과 규모(관계 수)',
        f'h{h}w{w}': '생성에 사용한 crop 사이즈'},
    'DESCRIPTION': {
        'WHAT': 'szmc v0의 이미지-마스크 쌍을 이용하여 생성한 crop에 대해, 자동으로 생성한 텍스트 존재성(o/x) 어노테이션',
        'WHY': '만화 이미지의 텍스트 존재성 분류 학습을 위해서 생성함',
        'KNWON_ERRORS':
        ( '이 데이터로 학습 가능한 예상되는 최고 정확도는 0.978임.'
        + ' has_text.manual.1_1000에서 생성한 GT를 쓰기 때문.')},
    'HOW_TO_GEN': {
        f'img_path.text_ox.h{h}w{w}':
        (f'python main.py data annotate_text_ox szmc_v0 DATA_SRC {h} {w}'
        + '# crop된 이미지 중에서 (h,w) 크기가 아닌 이미지는 제외됨.')},
    'special_values': {
        'num_has_text': len(fp.lfilter(fp.identity, has_texts)),
        'num_no_text': len(fp.lremove(fp.identity, has_texts))},
    'RELATIONS': {f'img_path.text_ox.h{h}w{w}': img_tfs}}

    rel_name = f'text_ox.auto.h{h}w{w}.v{version}.yml'
    Path(rels_dir, rel_name).write_text(
        yaml.dump(rel_dic, allow_unicode=True))

    # code for manual annotation and experiments. 
    #img_seq = (cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB) for p in org_crop_paths) # TODO: rgba?
    # __manual_has_text_annotation1000_from_m101_h256w256(img_seeq, mask_seq)
        
    
#----------------------------------------------------------------
def __manual_has_text_annotation1000_from_m101_h256w256(iseq, mseq):
    # 간단한 어노테이터 코드
    '''
    idxes = []
    sums = []
    import funcy as F
    for idx,(i,m) in enumerate(F.take(1000,zip(iseq,mseq))):
        print('1s:', m.sum(), end=' => ', flush=True)
        cv2.imshow('i', i)
        k = cv2.waitKey()
        if k == ord('x'):
            idxes.append(idx)
            sums.append(m.sum())
        print(chr(k))
    print('idxes =', idxes)
    print(sum(sums) / len(sums), 'sums =', sums)
    '''
    # best thershold 알아내기 실험
    '''
    ss = [m.sum() for m in fp.take(1000,mseq)]
    #thr = 32540.48780487805
    #thrs = list(range(10000, 1000000, 100))
    thrs = [333500]
    ans_rates = []
    for thr in thrs:
        #thr = 1008789.09574468085 
        #thr = 18789.09574468085 
        #thr = 1
        from pprint import pprint
        no_texts_auto = [s < thr for s in ss]
        no_texts_manual = [False] * len(no_texts_auto)
        #for idx in [2, 3, 4, 5, 7, 10, 11, 12, 13, 15, 18, 19, 20, 21, 24, 25, 26, 27, 28, 34, 35, 36, 39, 43, 44, 47, 49, 50, 51, 52, 55, 59, 60, 67, 68, 74, 79, 81, 87, 88, 96]:
        for idx in idxes:
            no_texts_manual[idx] = True
        #matcheds = fp.lmap(lambda a,b: a == b, no_texts_auto, no_texts_manual)
        matcheds = fp.lmap(fp.equal, no_texts_auto, no_texts_manual)
        print(matcheds)
        n_eqs = len(fp.lfilter(fp.identity, matcheds))
        n_neqs = len(fp.lremove(fp.identity, matcheds))
        print(n_eqs, n_neqs)
        print(n_eqs / len(matcheds), n_neqs / len(matcheds))
        ans_rates.append(n_eqs / len(matcheds))
        #print(' True:', len(fp.lfilter(fp.identity, chks)))
        #print('False:', len(fp.lremove(fp.identity, chks)))

    import matplotlib.pyplot as plt
    plt.plot(thrs, ans_rates)
    plt.show()
    print(sorted(zip(thrs, ans_rates), key=lambda ta: ta[1])[-1])
    return no_text_idxes
    '''
