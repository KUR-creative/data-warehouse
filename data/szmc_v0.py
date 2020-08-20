import os
from pathlib import Path

import cv2
import imagesize

from tasks import gen_crops
from utils import file_utils as fu, fp


#---------------------------------------------------------------
def save_crops(DATA_dir, h, w): # TODO: refactor
    # Get src images
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

    iseq = (cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB)
            for p in org_crop_paths) # TODO: rgba?
    mseq = (cv2.cvtColor(cv2.imread(p), cv2.COLOR_BGR2RGB)
            for p in mask_crop_paths) # TODO: rgba?
    '''
    idxes = []
    sums = []
    import funcy as F
    for idx,(i,m) in enumerate(F.drop(526,zip(iseq,mseq))):
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
        idxes = [2, 3, 4, 5, 7, 10, 11, 12, 13, 15, 18, 19, 20, 21, 24, 25, 26, 27, 28, 34, 35, 36, 39, 43, 44, 47, 49, 50, 51, 52, 55, 59, 60, 67, 68, 74, 79, 81, 87, 88, 96, 105, 106, 107, 109, 110, 113, 114, 115, 116, 117, 118, 121, 122, 123, 124, 129, 130, 131, 132, 139, 140, 141, 142, 154, 157, 160, 161, 162, 163, 164, 165, 166, 168, 171, 172, 173, 174, 176, 177, 178, 179, 180, 181, 184, 185, 186, 187, 188, 189, 192, 194, 195, 196, 197, 199, 200, 202, 203, 204, 205, 206, 207, 208, 210, 211, 212, 213, 214, 215, 216, 217, 218, 223, 224, 225, 230, 231, 232, 233, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 271, 272, 273, 274, 275, 276, 279, 280, 281, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 303, 304, 305, 306, 307, 311, 314, 315, 318, 319, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 338, 346, 349, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 363, 364, 365, 366, 367, 368, 369, 371, 372, 373, 374, 375, 376, 379, 380, 381, 382, 383, 384, 387, 388, 389, 390, 391, 392, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 410, 411, 412, 416, 417, 418, 419, 420, 422, 423, 424, 425, 426, 427, 428, 430, 431, 434, 435, 436, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 459, 460, 461, 462, 463, 464, 467, 468, 469, 470, 471, 472, 473, 475, 476, 477, 478, 479, 480, 483, 484, 485, 486, 488, 489, 491, 492, 493, 494, 495, 496, 499, 500, 501, 502, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 530, 531, 532, 533, 534, 535, 536, 538, 539, 540, 541, 542, 543, 544, 546, 547, 548, 549, 551, 552, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 599, 600, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 615, 617, 618, 619, 620, 621, 622, 623, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 638, 640, 641, 642, 643, 644, 645, 646, 648, 649, 650, 651, 652, 653, 654, 656, 657, 658, 659, 660, 661, 662, 664, 666, 667, 668, 672, 674, 680, 681, 682, 683, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 699, 701, 702, 703, 705, 706, 707, 709, 713, 721, 723, 724, 725, 726, 727, 729, 731, 732, 733, 734, 735, 741, 749, 754, 755, 756, 757, 758, 759, 762, 764, 765, 766, 767, 770, 772, 773, 774, 775, 778, 781, 782, 784, 786, 794, 795, 796, 797, 802, 803, 804, 805, 808, 809, 810, 811, 812, 813, 816, 817, 818, 819, 820, 821, 824, 825, 826, 827, 828, 829, 832, 834, 835, 836, 837, 838, 839, 840, 842, 843, 844, 845, 846, 847, 848, 850, 851, 852, 853, 854, 855, 858, 862, 863, 866, 870, 871, 873, 874, 882, 884, 885, 887, 890, 892, 893, 898, 899, 900, 901, 902, 903, 904, 905, 906, 907, 908, 910, 911, 912, 913, 914, 925, 931, 933, 934, 940, 941, 942, 943, 945, 948, 949, 950, 951, 952, 954, 956, 957, 958, 959, 961, 962, 964, 968, 969, 970, 971, 972, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982, 984, 985, 986, 987, 988, 989, 990, 992, 993, 994, 995, 996, 997, 998]
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


def manual_has_text_annotation1000_from_m101_h256w256():
    #직접 어노테이션한 결과 텍스트가 없는 이미지의 인덱스(256x crop만): 
    no_text_idxes = [2, 3, 4, 5, 7, 10, 11, 12, 13, 15, 18, 19, 20, 21, 24, 25, 26, 27, 28, 34, 35, 36, 39, 43, 44, 47, 49, 50, 51, 52, 55, 59, 60, 67, 68, 74, 79, 81, 87, 88, 96, 105, 106, 107, 109, 110, 113, 114, 115, 116, 117, 118, 121, 122, 123, 124, 129, 130, 131, 132, 139, 140, 141, 142, 154, 157, 160, 161, 162, 163, 164, 165, 166, 168, 171, 172, 173, 174, 176, 177, 178, 179, 180, 181, 184, 185, 186, 187, 188, 189, 192, 194, 195, 196, 197, 199, 200, 202, 203, 204, 205, 206, 207, 208, 210, 211, 212, 213, 214, 215, 216, 217, 218, 223, 224, 225, 230, 231, 232, 233, 237, 238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 271, 272, 273, 274, 275, 276, 279, 280, 281, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298, 299, 303, 304, 305, 306, 307, 311, 314, 315, 318, 319, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, 331, 332, 333, 334, 335, 338, 346, 349, 352, 353, 354, 355, 356, 357, 358, 359, 360, 361, 363, 364, 365, 366, 367, 368, 369, 371, 372, 373, 374, 375, 376, 379, 380, 381, 382, 383, 384, 387, 388, 389, 390, 391, 392, 394, 395, 396, 397, 398, 399, 400, 401, 402, 403, 404, 410, 411, 412, 416, 417, 418, 419, 420, 422, 423, 424, 425, 426, 427, 428, 430, 431, 434, 435, 436, 440, 441, 442, 443, 444, 445, 446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 459, 460, 461, 462, 463, 464, 467, 468, 469, 470, 471, 472, 473, 475, 476, 477, 478, 479, 480, 483, 484, 485, 486, 488, 489, 491, 492, 493, 494, 495, 496, 499, 500, 501, 502, 504, 505, 506, 507, 508, 509, 510, 511, 512, 513, 514, 515, 516, 518, 519, 520, 521, 522, 523, 524, 525, 526, 527, 528, 530, 531, 532, 533, 534, 535, 536, 538, 539, 540, 541, 542, 543, 544, 546, 547, 548, 549, 551, 552, 554, 555, 556, 557, 558, 559, 560, 561, 562, 563, 564, 565, 567, 568, 569, 570, 571, 572, 573, 574, 575, 576, 577, 578, 579, 580, 581, 582, 583, 584, 586, 587, 588, 589, 590, 591, 592, 593, 594, 595, 596, 599, 600, 602, 603, 604, 605, 606, 607, 608, 609, 610, 611, 612, 615, 617, 618, 619, 620, 621, 622, 623, 626, 627, 628, 629, 630, 631, 632, 633, 634, 635, 636, 638, 640, 641, 642, 643, 644, 645, 646, 648, 649, 650, 651, 652, 653, 654, 656, 657, 658, 659, 660, 661, 662, 664, 666, 667, 668, 672, 674, 680, 681, 682, 683, 685, 686, 687, 688, 689, 690, 691, 692, 693, 694, 695, 699, 701, 702, 703, 705, 706, 707, 709, 713, 721, 723, 724, 725, 726, 727, 729, 731, 732, 733, 734, 735, 741, 749, 754, 755, 756, 757, 758, 759, 762, 764, 765, 766, 767, 770, 772, 773, 774, 775, 778, 781, 782, 784, 786, 794, 795, 796, 797, 802, 803, 804, 805, 808, 809, 810, 811, 812, 813, 816, 817, 818, 819, 820, 821, 824, 825, 826, 827, 828, 829, 832, 834, 835, 836, 837, 838, 839, 840, 842, 843, 844, 845, 846, 847, 848, 850, 851, 852, 853, 854, 855, 858, 862, 863, 866, 870, 871, 873, 874, 882, 884, 885, 887, 890, 892, 893, 898, 899, 900, 901, 902, 903, 904, 905, 906, 907, 908, 910, 911, 912, 913, 914, 925, 931, 933, 934, 940, 941, 942, 943, 945, 948, 949, 950, 951, 952, 954, 956, 957, 958, 959, 961, 962, 964, 968, 969, 970, 971, 972, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982, 984, 985, 986, 987, 988, 989, 990, 992, 993, 994, 995, 996, 997, 998]
    #1000개 중 2개의 잘못된 어노테이션 포함됨.
    '''
    이론적으로는 99.8% 정확도가 최고임.
    
    segnet 데이터셋의 마스크를 이용하여 자동 생성된 어노테이션의 경우
    threshold는 333500(8bit rgb mask), 정확도는 0.978.
    (8bit png의 1 개수로 확인)
    
    즉 이 데이터셋으로 has_text/no_text를 분류할 경우 
    0.97~0.98 정도가 가능한 최고 정확도일 수 있음.
    '''
    
    '''
    # 간단한 어노테이터 코드
    idxes = []
    sums = []
    import funcy as F
    for idx,(i,m) in enumerate(F.drop(526,zip(iseq,mseq))):
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
        
#---------------------------------------------------------------
def _gen_crops(root, img_dir, h, w, dst_dir=None):
    # Get src images
    assert img_dir.exists()
    
    crop_dir = Path(root, 'crop')
    dst_crops_dir = crop_dir / f'{img_dir.stem}.h{h}w{w}'
    
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
    
    print(f'start: _gen_crops({root}, {img_dir}, {h}, {w}, {dst_dir})')
    for path, crop in path_crop_seq:
        cv2.imwrite(path, cv2.cvtColor(crop, cv2.COLOR_RGB2BGR))
    print('finished')
