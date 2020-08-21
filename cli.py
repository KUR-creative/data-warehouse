from pathlib import Path
from importlib import import_module
import sys

import yaml


def check_and_write_log(logging, data_source):
    ''' Convenient helper function. '''
    if logging:
        write_log(Path(data_source, 'META', 'log.yml'), sys.argv)
        
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

#----------------------------------------------------------------
class interface(object):
    data = data
