from pathlib import Path
from importlib import import_module
import sys
import shutil

import yaml
from tqdm import tqdm

from dataset import img_text_ox, img_only, crop_only
from out import tfrecord as tfrec
from utils import file_utils as fu
from utils import image_utils as iu
from utils.etc_utils import git_hash
import tasks
import tasks.map_imgs

import core
import core.path
import core.name
import core.io

#----------------------------------------------------------------
def assert_valid_data_source(data_src_dir_path):
    assert Path(data_src_dir_path).exists()
    assert Path(data_src_dir_path).is_absolute()
    assert Path(data_src_dir_path, 'DATA').exists()
    assert Path(data_src_dir_path, 'META').exists()
    assert Path(data_src_dir_path, 'RELS').exists()

def assert_valid_dset_root(dset_dir_path):
    assert Path(dset_dir_path).exists()
    assert Path(dset_dir_path).is_absolute()
    assert Path(dset_dir_path, 'DSET').exists()
    assert Path(dset_dir_path, 'META').exists()
    assert Path(dset_dir_path, 'OUTS').exists()

def check_and_write_dw_log(logging):
    ''' Convenient helper func to log dw.log.yml '''
    if logging:
        write_log('dw.log.yml', sys.argv + [f'#{git_hash()}'])
        
def check_and_write_log(logging, out_dir):
    ''' Convenient helper func. out_dir must have 'META' dir. '''
    if logging and out_dir:
        write_log(Path(out_dir, 'META', 'log.yml'),
                  sys.argv + [f'#{git_hash()}'])
        
def write_log(log_path, content):
    ''' Append or create content to log. content is just py obj. '''
    mode = 'a' if Path(log_path).exists() else 'w'
    with open(log_path, mode) as log:
        log.write('- ')
        log.write(yaml.dump(content,
                            allow_unicode=True,
                            default_flow_style=True))

#----------------------------------------------------------------
class data(object):
    ''' Add data to data-sources '''
    @staticmethod
    def gen_1bit_masks(mask_dir, dst_dir=None, channel=0,
                       exist_ok=False,
                       note=None, logging=True):
        '''
        마스크가 저장된 디렉토리 mask_dir에서 마스크를 로드(rgb)하여 
        channel을 잘라내고 dst_dir에 저장한다.
        
        mask_dir 내부에 존재하는 모든 마스크가 재귀적으로 로드된다.
        mask_dir 내부 디렉토리 구조 또한 복사된다.
        dst_dir이 존재하지 않으면 새로 생성된다.
        dst_dir=None이면 {mask_dir}.ch{channel}로 이름이 붙는다.
        
        args:
        mask_dir: 마스크들이 저장된 폴더의 경로. 
        dst_dir: 1bit 마스크를 저장할 폴더의 경로. 기본: {mask_dir}.ch{channel}
        channel: 이미지에서 잘라낼 채널. [0,1,2] 중 선택(rgb)
        exist_ok: dst_dir이 존재해도 처리를 할지 결정. 기본: False
        '''
        if dst_dir is None:
            src = str(Path(mask_dir)) # Remove path sep thingy
            dst_dir = f'{src}.ch{channel}' # TODO: Can refactor?
        mask_pathseq = tasks.map_imgs.mask1bit_dstpath_pairseq(
            mask_dir, dst_dir, channel) # <mask, path>
        
        fu.copy_dirtree(mask_dir, dst_dir, dirs_exist_ok=exist_ok)

        print('Generate 1 bit masks...')
        for mask, path in mask_pathseq:
            iu.cv.write_png1bit(path, mask)
        print('Done!')
            
        data_source = core.path.data_source(mask_dir)
        check_and_write_log(logging, data_source)
        check_and_write_dw_log(logging)

    @staticmethod
    def crops_dir(img_root, crop_h, crop_w,
                  pad_mode='crop_maximum',
                  dst_root='', exist_ok=False,
                  note=None, logging=True):
        '''
        img_root의 모든 이미지를 crop하고 dst_root로 재귀적으로 저장. 
        img_root의 디렉토리 구조가 보존된다.
        
        crop 파일 이름은 원본 이미지 이름에 .y{y}x{x}를 붙인다.
        만일 이미지가 crop_h, crop_w보다 작다면, 
        패딩하여 크기를 늘린 이미지가 저장된다.
        
        args:
        img_root: 이미지가 저장되어 있는 디렉토리, 어떤 구조라도 허용.
        crop_h: crop의 height.
        crop_w: crop의 width.
        pad_mode: 문자열로 pad mode를 정의할 수 있다. 
        기본은 일반적인 만화 이미지에서 쓰는 crop_maximum으로, crop의
        최대 값으로 pad한다(np.pad에 없는 mode임)
        dst_root: crop을 저장할 디렉토리 경로.
        exist_ok: dst_root가 존재해도 처리를 할지 결정. 기본: False
        기본값은 img_root.h{crop_h}w{crop_w}로 저장된다.
        '''
        assert Path(img_root).exists()
        assert Path(img_root).is_dir()
        if not dst_root:
            path = fu.path_str(img_root)
            dst_root = path + f'.h{crop_h}w{crop_w}'
        num_mappings, cropseq, dst_pathseq = \
            tasks.map_imgs.recur_cropseq(
                img_root, dst_root, crop_h, crop_w,
                pad_mode=pad_mode)
        
        fu.copy_dirtree(img_root, dst_root, dirs_exist_ok=exist_ok)
        for crop, dst_path in tqdm(zip(cropseq, dst_pathseq),
                                   desc='Crop and Save images',
                                   total=num_mappings):
            #print(dst_path); cv2.imshow('c', crop); cv2.waitKey(0)
            iu.cv.write_rgb(dst_path, crop)
        print('Done!')
        
        data_source = core.path.data_source(img_root)
        if data_source:
            check_and_write_log(logging, data_source)
        check_and_write_dw_log(logging)
    
    @staticmethod
    def copy_hw_images(height, width, src_dir, dst_dir=None,
                       note=None, logging=True):
        '''
        크기가 h,w인 이미지만 src_dir에서 dst_dir로 복사한다. 
        디렉토리 구조가 유지된다.
        
        args:
        height: 이미지 height
        width: 이미지 width
        src_dir: 복사할 디렉토리 경로
        dst_dir: SRC_DIR을 붙여 넣을 디렉토리. None이라면 src_dir에 
                 '.strict_hw'가 붙는다.
        '''
        dst_dir = str(Path(src_dir)) + '.strict_hw'
        shutil.copytree(src_dir, dst_dir)
        
        import imagesize
        small_img_paths = list(filter(
            lambda p: imagesize.get(p) != (width, height),
            fu.descendants(dst_dir)))
        for path in small_img_paths:
            Path(path).unlink()
            
        # TODO: Add data_source logging
        check_and_write_dw_log(logging)
    
    @staticmethod
    def crops(module, data_source, crop_h, crop_w, *args,
              note=None, logging=True):
        '''
        [DEPRECATED!] 잘린 이미지(crops) 데이터 생성
        
        데이터 소스(DATA_SOURCE)로부터, MODULE에서 정의한 대로 이미지를 
        가져오고, (CROP_H, CROP_W)로 자른 후, MODULE에 정의된 곳에 
        저장한다.
        
        데이터 소스는 DATA, META, RELS 폴더를 가지는 폴더이다. 
        
        args:
        module: data load/proces/save를 정의하는 dw.data 패키지의 모듈.
        data_source: 처리하려는 데이터 소스의 경로.
        crop_h: crop의 height.
        crop_w: crop의 width.
        *args: generate_crops의 추가적인 인자. MODULE을 참고할 것.
        note: 이 작업에 대한 추가적인 설명.
        logging: False일 경우 로깅하지 않음
        '''
        assert_valid_data_source(data_source)
        
        m = import_module(f'data.{module}', 'data')
        m.generate_crops(data_source, crop_h, crop_w, *args)
        
        check_and_write_log(logging, data_source)
        check_and_write_dw_log(logging)
            
    @staticmethod
    def annotate_text_ox(module,
                         data_source, crop_h, crop_w, *args,
                         note=None, logging=True):
        '''
        텍스트 존재성 어노테이션 데이터(관계) 생성
        
        데이터 소스(DATA_SOURCE)와 CROP_H, CROP_W를 이용하여
        어노테이션을 할 crop 이미지들을 결정한다. 이후 MODULE에 정의된 
        방식으로 자동적으로 어노테이션을 생성하고, DATA_SOURCE/RELS 아래에
        저장한다.(저장 파일 이름 또한 MODULE에서 결정)
        
        args:
        module: data load/proces/save를 정의하는 dw.data 패키지의 모듈.
        data_source: 처리하려는 데이터 소스의 경로.
        crop_h: crop의 height. DATA_SOURCE와 함께 crop 이미지가 있는 폴더를 결정함.
        crop_w: crop의 width. DATA_SOURCE와 함께 crop 이미지가 있는 폴더를 결정함.
        *args: annotate_text_ox의 추가적인 인자. MODULE을 참고할 것.
        note: 이 작업에 대한 추가적인 설명.
        logging: False일 경우 로깅하지 않음
        '''
        assert_valid_data_source(data_source)
        
        m = import_module(f'data.{module}', 'data')
        m.annotate_text_ox(data_source, crop_h, crop_w, *args)
        
        check_and_write_log(logging, data_source)
        check_and_write_dw_log(logging)
        
    @staticmethod
    def canonical_select_file(module, select_file, out_path=None,
                              note=None, logging=True):
        '''
        옛 메타 데이터 파일로부터 통일된 형식의 R/D/T 선택 파일을 생성한다.
        
        일종의 임시 스크립트이며, 일반적인 명령과는 거리가 멀다.
        module은 clean_fmd_comics와 old_snet를 쓸 수 있다.
        
        이 select 파일을 이용하여 데이터셋을 만들어 학습하면 
        과거 모델의 실험 결과와 비교할 수 있다.
        '''
        data_source = core.path.data_source(select_file)
        assert_valid_data_source(data_source)
        
        m = import_module(f'data.{module}', 'data')
        m.canonical_select(data_source, select_file, out_path)

        check_and_write_log(logging, data_source)
        check_and_write_dw_log(logging)
        
class dset(object):
    ''' Generate and Save dataset from data-sources '''

    @staticmethod
    def text_ox(dset_root, select,
                train_ratio, dev_ratio, test_ratio,
                rel_file_name, *data_source_dirs,
                note=None, logging=True):
        '''
        (이미지: 텍스트 존재성) 데이터셋 생성
        
        [[이미지, 텍스트 존재성]] 관계에 대한 어노테이션 yml이 존재하는
        데이터 소스(data_source_dirs)들로부터 tRain/Dev/Test로 
        쪼개진 데이터셋을 생성하고 out_dset_dir에 적절한 이름으로
        저장한다.
        
        args:
        dset_root: 생성한 데이터셋 yml 파일이 저장되는 DSET, META, OUTS을 포함하는 폴더.
        select: tRain/Dev/Test를 선택하는 함수. 현재 random_select만 지원. 
                SELECT_FN이 정의된 모듈을 참조할 것.
        train_ratio: 학습 데이터의 비율, 정수. 내부적으로는 R / (R + D + T)로 계산한다.
        dev_ratio: 개발 데이터의 비율, 정수. 내부적으로는 D / (R + D + T)로 계산한다.
        test_ratio: 테스트 데이터의 비율, 정수. 내부적으로는 T / (R + D + T)로 계산한다.
        rel_file_name: data_source_dir/RELS에 존재하는 yml 중 처리하길 원하는 파일의 이름.
                       만일 RELS 아래 폴더에 포함된 파일이면, 폴더 또한 경로에 포함한다.
                       즉 RELS에 상대적인 경로이다. 
        *data_source_dirs: 처리를 원하는 데이터 소스들(DATA, META, RELS 포함). 하나 이상이 포함될 수 있다.
                           RELS 아래에 REL_FILE_NAME을 만족하는 파일이 있어야 한다.
        note: 이 작업에 대한 추가적인 설명.
        logging: False일 경우 로깅하지 않음
        '''
        assert_valid_dset_root(dset_root)
        assert len(data_source_dirs) > 0
        img_text_ox.generate(
            dset_root, select,
            (train_ratio, dev_ratio, test_ratio),
            rel_file_name, *data_source_dirs)
        
        check_and_write_log(logging, dset_root)
        check_and_write_dw_log(logging)
        
    @staticmethod
    # TODO         dset_path - yaml path to save  
    def image_only(dset_root, dset_name,
                   img_root, select='random_select',
                   has_text=None,
                   crop_h=None, crop_w=None,
                   note=None, logging=True):
        '''
        표준 데이터 형태(canonical form)의 image_only 데이터셋 생성
        
        결과는 
        dset_root/DSET/dset_name.img_only.h{crop_h}w{crop_w}.r_s.r_s.r_s.yml
        로 저장된다.
        
        표준 데이터 형태는 브랜치 12-snet-dataset(PR 18)부터 적용된다.
        식질머신에서 사용되는 대부분의 데이터를 표현할 수 있다.
        
        args:
        dset_root: 데이터셋 폴더. DSET, OUTS, META 폴더를 포함함.
        dset_name: 생성하는 데이터셋 이름. 
        img_root: 처리하려는 이미지가 있는 폴더를 모두 포함하는 폴더.
                  재귀적으로 모든 이미지를 처리한다.
        select: R/D/T 선택 방법. select_yml을 넣으면 그걸 씀. 기본은 무작위 선택 (미구현)
        has_text: 전체 이미지에 텍스트 유(o) 무(x) 알수없음(?). None일 경우 데이터에 포함되지 않음 (미구현)
        crop_h: crop의 세로 길이. None인 경우는 전체 크기 사용 (미구현)
        crop_w: crop의 세로 길이. None인 경우는 전체 크기 사용 (미구현)
        note: 이 작업에 대한 추가적인 설명.
        logging: False일 경우 로깅하지 않음
        '''
        data_source = core.path.data_source(img_root)
        assert_valid_data_source(data_source)
        assert_valid_dset_root(dset_root)

        dset_dic = img_only.generate(
            img_root, select, has_text, crop_h, crop_w)
        dset_name = core.name.dset_name(
            'fmd','img_only', (crop_h,crop_w), (0,0,0), dset_dic)
        core.io.dump_data_yaml(
            Path(dset_root, 'DSET', dset_name), dset_dic)
        
        check_and_write_log(logging, dset_root)
        check_and_write_dw_log(logging)

    @staticmethod
    def crop_only(dset_root, dset_name,
                  crops_root, select='random_select',
                  note=None, logging=True):
        '''
        crop만 존재하는 폴더(crops_root)로부터
        표준 데이터 형태(canonical form)의 crop_only 데이터셋 생성
        crops_root 내부의 모든 crop은 크기(h,w)가 같아야 한다.
        
        결과는 
        dset_root/DSET/{dset_name}.crop_only.h{crop_h}w{crop_w}.r_s.r_s.r_s.yml
        로 저장된다.
        
        표준 데이터 형태는 브랜치 12-snet-dataset(PR 18)부터 적용된다.
        식질머신에서 사용되는 대부분의 데이터를 표현할 수 있다.
        
        args:
        dset_root: 데이터셋 폴더. DSET, OUTS, META 폴더를 포함함.
        dset_name: 생성하는 데이터셋 이름. 
        crops_root: 처리하려는 crop이 있는 폴더를 모두 포함하는 폴더.
                    재귀적으로 모든 이미지를 처리한다.
        select: R/D/T 선택 방법. select_yml을 넣으면 그걸 씀. 기본은 무작위 선택 (미구현)
        note: 이 작업에 대한 추가적인 설명.
        logging: False일 경우 로깅하지 않음
        '''
        assert_valid_dset_root(dset_root)
        assert Path(crops_root).exists()
        
        dset_dic = crop_only.generate(crops_root, select)
        dset_name = core.name.dset_name(
            'fmd','crop_only',
            (dset_dic['crop_h'], dset_dic['crop_w']), (0,0,0),
            dset_dic)
        print('Dump dataset yml...')
        core.io.dump_data_yaml(
            Path(dset_root, 'DSET', dset_name), dset_dic)
        print('Done!')
        
        check_and_write_log(logging, dset_root)
        check_and_write_dw_log(logging)


    @staticmethod
    def merge(module, dset_root, *dset_yml_paths,
              note=None, logging=True):
        '''
        데이터셋 여럿을 합친 데이터셋 생성
        
        args:
        module: 합쳐진 데이터셋의 이름과 기타 등등을 결정하는 모듈
        dset_root: 생성한 데이터셋 yml 파일이 RELS 아래에 저장되는 (DSET, META, OUTS)을 포함하는 폴더.
        *dset_yml_paths: 합치려는 데이터셋들의 yml 경로들
        note: 이 작업에 대한 추가적인 설명.
        logging: False일 경우 로깅하지 않음
        '''
        assert_valid_dset_root(dset_root)
        
        m = import_module(f'dataset.{module}', 'dataset')
        m.merge(dset_root, *dset_yml_paths)
        
        check_and_write_log(logging, dset_root)
        check_and_write_dw_log(logging)
                   
class out(object):
    ''' Export dataset as learnable artifact(s) '''
    
    @staticmethod
    def united_tfrecord(dset_path, out_path='',
                        note=None, logging=True):
        dset_path = Path(dset_path)
        assert dset_path.exists()
        dset_root = Path(core.path.dataset_root(dset_path))
        assert_valid_dset_root(dset_root)

        out_path = str(
            Path(out_path).resolve() if out_path else
            dset_root / 'OUTS' / f'{dset_path.stem}.tfrecord')
        tfrec.gen_and_save(dset_path, out_path)
        
    @staticmethod
    def flist(dset_path, out_dir='', note=None, logging=True):
        '''
        몇몇 모델에서 원하는 flist 파일 3개(R/D/T) 생성. 
        현재는 crop_only만 지원.
        
        dset_path: crop_only 데이터셋 경로
        out_dir: 없으면 dset_root 구해서 그 아래 /OUTS에 저장.
        '''
        dset_path = Path(dset_path)
        assert dset_path.exists()
        dset_root = Path(core.path.dataset_root(dset_path))
        assert_valid_dset_root(dset_root)
        
        if not out_dir:
            out_dir = dset_root / 'OUTS' 
        with open(dset_path) as f:
            dset = yaml.safe_load(f)

        stem_parts = dset_path.stem.split('.')
        test_rs = stem_parts[-1] # rs: revision_size
        dev_rs = stem_parts[-2]
        train_rs = stem_parts[-3]
        except_rdt = '.'.join(stem_parts[:-3])
        
        train_flist_path = Path(
            out_dir,
            '.'.join([except_rdt, 'train', train_rs, 'flist']))
        dev_flist_path = Path(
            out_dir,
            '.'.join([except_rdt, 'dev', dev_rs, 'flist']))
        test_flist_path = Path(
            out_dir,
            '.'.join([except_rdt, 'test', test_rs, 'flist']))
        
        train_flist_path.write_text('\n'.join(dset['TRAIN']))
        dev_flist_path.write_text('\n'.join(dset['DEV']))
        test_flist_path.write_text('\n'.join(dset['TEST']))
        
        check_and_write_log(logging, dset_root)
        check_and_write_dw_log(logging)
        
    @staticmethod
    def text_ox(out_form, dset_path, out_path='',
                note=None, logging=True):
        '''
        (이미지: 텍스트 존재성) 데이터셋 export
        
        [[이미지, 텍스트 존재성]] 데이터셋 yml(DSET_PATH)에서 
        OUT_FORM 형식의 학습 가능한 아티팩트를 OUT_PATH에 저장한다.
        (현재 tfrecord만 지원)
        
        OUT_PATH는 비워두고, 다음과 같이 실행할 것을 권장함.
        python main.py out text_ox tfrecord $dp   --note='...'
        
        args:
        out_form: 저장 가능한 아티팩트 형식, 현재 tfrecord만 지원.
        dset_path: 데이터셋 yml의 경로.
        out_path: 출력할 위치. 기본 값으로는 DSET_PATH에서 DSET을 
        OUTS로 바꾸고 extension을 수정한 경로. 부모 dir이 반드시
        DSET, META, OUTS 디렉토리를 가져야 한다. 
        note: 이 작업에 대한 추가적인 설명.
        logging: False일 경우 로깅하지 않음
        '''
        if out_form != 'tfrecord':
            raise NotImplementedError(
                "Currently only 'tfrecord' is supported")
        
        dp = Path(dset_path)
        dset_path = str(dp.resolve())
        
        dset_root = Path(*dp.parts[:-2])
        out_path = str(
            Path(out_path).resolve() if out_path else
            dset_root / 'OUTS' / f'{dp.stem}.{out_form}')
        if not out_path:
            assert_valid_dset_root(dset_root)

        img_text_ox.output(dset_path, out_path)

        check_and_write_log(logging, dset_root)
        check_and_write_dw_log(logging)
        
class script(object):
    from scripts import move_danbooru_crops as _
    move_danbooru_crops = staticmethod(_.main)
    #from scripts import dummy as _ # It works well!
    #dummy = staticmethod(_.main)
        
def _history(log_path='dw.log.yml'):
    '''
    Print previously executed commands
    
    args:
    log_path: log file path
    '''
    assert Path(log_path).exists()
    with open(log_path) as f:
        cmd_args_lst = yaml.safe_load(f)

    #print(cmd_args_lst)
    print('\n'.join([' '.join(['python', *args])
                     for args in cmd_args_lst]))


#----------------------------------------------------------------
class interface(object):
    data = data
    dset = dset
    out = out
    history = staticmethod(_history)
    hist = staticmethod(_history)
    script =  script
