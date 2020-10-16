from pathlib import Path

def main(root, max_id, n_digits):
    ''' 
    main('./root', 12340, 3); then Creates dirs:
    ./root/000
    ./root/001
    ...
    ./root/999
    '''
    limit = 10**n_digits
    assert max_id >= limit

    dir_paths =[Path(root, f'%0{n_digits}d' % i)
                for i in range(0, limit)]
    for dir_path in dir_paths:
        dir_path.mkdir(parents=True)
