from pathlib import Path
from importlib import import_module
import sys
import shutil

import yaml

from dataset import img_text_ox
from utils import file_utils as fu
from utils.etc_utils import git_hash

def assert_valid_data_source(data_src_dir_path):
    assert Path(data_src_dir_path).exists()
    assert Path(data_src_dir_path).is_absolute()
    assert Path(data_src_dir_path, 'DATA').exists()
    assert Path(data_src_dir_path, 'META').exists()
    assert Path(data_src_dir_path, 'RELS').exists()

def assert_valid_dset_directory(dset_dir_path):
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
    if logging:
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

class data(object):
    ''' Add data to data-sources '''
    
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
            
        check_and_write_dw_log(logging)
    
    @staticmethod
    def crops(module, data_source, crop_h, crop_w, *args,
              note=None, logging=True):
        '''
        잘린 이미지(crops) 데이터 생성
        
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

class dset(object):
    ''' Generate and Save dataset from data-sources '''
    @staticmethod
    def text_ox(out_dset_dir, select,
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
        out_dset_dir: 생성한 데이터셋 yml 파일이 저장되는 DSET, META, OUTS을 포함하는 폴더.
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
        assert_valid_dset_directory(out_dset_dir)
        assert len(data_source_dirs) > 0
        img_text_ox.generate(
            out_dset_dir, select,
            (train_ratio, dev_ratio, test_ratio),
            rel_file_name, *data_source_dirs)
        
        check_and_write_log(logging, out_dset_dir)
        check_and_write_dw_log(logging)

    @staticmethod
    def merge(module, out_dset_dir, *dset_yml_paths,
              note=None, logging=True):
        '''
        데이터셋 여럿을 합친 데이터셋 생성
        
        args:
        module: 합쳐진 데이터셋의 이름과 기타 등등을 결정하는 모듈
        out_dset_dir: 생성한 데이터셋 yml 파일이 RELS 아래에 저장되는 (DSET, META, OUTS)을 포함하는 폴더.
        *dset_yml_paths: 합치려는 데이터셋들의 yml 경로들
        note: 이 작업에 대한 추가적인 설명.
        logging: False일 경우 로깅하지 않음
        '''
        assert_valid_dset_directory(out_dset_dir)
        
        m = import_module(f'dataset.{module}', 'dataset')
        m.merge(out_dset_dir, *dset_yml_paths)
        
        check_and_write_log(logging, out_dset_dir)
        check_and_write_dw_log(logging)
                   
class out(object):
    ''' Export dataset as learnable artifact(s) '''
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
            assert_valid_dset_directory(dset_root)

        img_text_ox.output(dset_path, out_path)

        check_and_write_log(logging, dset_root)
        check_and_write_dw_log(logging)
        

#----------------------------------------------------------------
class interface(object):
    data = data
    dset = dset
    out = out
