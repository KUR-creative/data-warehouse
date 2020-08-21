from importlib import import_module

class data(object):
    ''' Add data to data-sources '''
    @staticmethod
    def crops(module, data_source, crop_h, crop_w):
        '''
        잘린 이미지(crops) 데이터 생성
        
        데이터 소스(DATA_SOURCE)로부터, MODULE에서 정의한 대로 이미지를 
        가져오고, (CROP_H, CROP_W)로 자른 후, MODULE에 정의된 곳에 
        저장한다.
        
        데이터 소스는 DATA, META, RELS 폴더를 가지는 폴더이다. 
        
        args:
        module: 데이터의 load/proces/save를 정의하는 data 패키지의 모듈.
        data_source: 처리하려는 데이터 소스의 경로.
        crop_h: crop의 height.
        crop_w: crop의 width.
        '''
        loaded_module = import_module(f'data.{module}', 'data')
        loaded_module.generate_crops(data_source, crop_h, crop_w)

#----------------------------------------------------------------
class interface(object):
    data = data
