from pathlib import Path

import core

def main(parent, max_id, n_digits):
    ''' 
    main('./parent', 12340, 3); then Creates dirs:
    ./parent/000
    ./parent/001
    ...
    ./parent/999
    '''
    limit = 10**n_digits
    assert max_id >= limit

    dir_paths = core.path.id_dirs(parent, n_digits)
    for dir_path in dir_paths:
        Path(dir_path).mkdir(parents=True)
