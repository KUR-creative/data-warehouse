import os

import pytest


def skipif_none(*candidates):
    for fixture in candidates:
        if fixture is None:
            pytest.skip('Some fixture is None')
            return
        
def env_val(**kv): # just one kward arg
    ''' Useage:  
    ```
    def test_some_pytest_case(fix, ture):
        fix = env_val(fix=fix)
        ture = env_val(ture=ture)
    ```
    if pytest fixture is None, return environ[key] or None.
    '''
    assert len(kv) == 1
    for k,v in kv.items():
        return os.environ.get(k) if v is None else v

#def fetch_env(**kv): # py 3.6+: kwargs order preserved
#    ''' key as variable name, value as value of variable '''
#    ks, vs = zip(*kv.items()) # unzip
#    return F.zipdict(
#        kv.keys(),
#        (env_val(k=v) for k,v in kv.items()))
