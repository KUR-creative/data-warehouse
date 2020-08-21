import os
from pathlib import Path

import cv2
import imagesize

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

def annotate_has_text(org_dir, mask_dir, h=None, w=None):
    ''' If h,w is passed, Use cropped directories. '''
    org_dir = Path(org_dir); mask_dir = Path(mask_dir)
    assert (h is None and w is None) or (h > 0 and w > 0)

    # Get cropped paths (TODO: would be extracted as a function)
    if h is not None and w is not None:
        org_stem = org_dir.stem + f'.h{h}w{w}'
        mask_stem = mask_dir.stem + f'.h{h}w{w}'
        org_dir = org_dir.parent / 'crop' / org_stem
        mask_dir = mask_dir.parent / 'crop' / mask_stem
    assert org_dir.exists(), org_dir
    assert mask_dir.exists(), mask_dir

    # Use only (h,w) sized crops
    org_paths = fu.human_sorted(fu.descendants(org_dir))
    mask_paths = fu.human_sorted(fu.descendants(mask_dir))
    assert len(org_paths) == len(mask_paths)
    def is_hw_size(path):
        img_w,img_h = imagesize.get(path)
        return img_w == w and img_h == h
    org_crop_paths = fp.lfilter(is_hw_size, org_paths)
    mask_crop_paths = fp.lfilter(is_hw_size, mask_paths)
    #for o,m in zip(org_crop_paths, mask_crop_paths): print(o,m)
    
    mask_seq = (cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB)
                for p in mask_crop_paths) # TODO: rgba?
    # Map mask_seq to has-text? (T/F)
    # Zip with org_crop_paths
    # Save to has_text.auto.1_{len(paths)}.yml

    # code for experiments. 
    #img_seq = (cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB) for p in org_crop_paths) # TODO: rgba?
    # manual_has_text_annotation1000_from_m101_h256w256(img_seeq, mask_seq)

def manual_has_text_annotation1000_from_m101_h256w256(iseq, mseq):
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
