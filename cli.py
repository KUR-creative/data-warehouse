from pathlib import Path
from importlib import import_module
import sys

import yaml

from dataset import img_text_ox


def check_and_write_dw_log(logging):
    ''' Convenient helper func to log dw.log.yml '''
    if logging:
        write_log('dw.log.yml', sys.argv)
        
def check_and_write_log(logging, out_dir):
    ''' Convenient helper func. out_dir must have 'META' dir. '''
    if logging:
        write_log(Path(out_dir, 'META', 'log.yml'), sys.argv)
        
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
    def crops(module, data_source, crop_h, crop_w,
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
        note: 이 작업에 대한 추가적인 설명.
        logging: False일 경우 로깅하지 않음
        '''
        assert Path(data_source).is_absolute()
        m = import_module(f'data.{module}', 'data')
        m.generate_crops(data_source, crop_h, crop_w)
        
        check_and_write_log(logging, data_source)
        check_and_write_dw_log(logging)
            
    @staticmethod
    def annotate_text_ox(module, data_source, crop_h, crop_w,
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
        note: 이 작업에 대한 추가적인 설명.
        logging: False일 경우 로깅하지 않음
        '''
        assert Path(data_source).is_absolute()
        m = import_module(f'data.{module}', 'data')
        m.annotate_text_ox(data_source, crop_h, crop_w)
        
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
        select: tRain/Dev/Test를 선택하는 함수. SELECT_FN이 정의된 모듈을 참조할 것.
        train_ratio: 학습 데이터의 비율, 정수. 내부적으로는 R / (R + D + T)로 계산한다.
        dev_ratio: 개발 데이터의 비율, 정수. 내부적으로는 D / (R + D + T)로 계산한다.
        test_ratio: 테스트 데이터의 비율, 정수. 내부적으로는 T / (R + D + T)로 계산한다.
        rel_file_name: data_source_dir/RELS에 존재하는 yml 중 처리하길 원하는 파일의 이름.
        data_source_dirs: 처리를 원하는 데이터 소스들 리스트.
        note: 이 작업에 대한 추가적인 설명.
        logging: False일 경우 로깅하지 않음
        '''
        assert len(data_source_dirs) > 0
        img_text_ox.generate(
            out_dset_dir, select,
            (train_ratio, dev_ratio, test_ratio),
            rel_file_name, *data_source_dirs)
        
        check_and_write_log(logging, out_dset_dir)
        check_and_write_dw_log(logging)
                   

#----------------------------------------------------------------
class interface(object):
    data = data
    dset = dset
