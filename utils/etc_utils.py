import funcy as F

def modulo_pad(x, m):
    ''' 2a = x + modulo_pad (mod m), where a < x < 2a '''
    return (m - (x % m)) % m

def factorseq(y, d):
    ''' Generate factor sequence: 0, d, 2d, ..., y - d '''
    assert y % d == 0
    
    beg = 0
    max = y
    while beg != max:
        yield beg
        beg += d
        
def partition(y, size):
    ''' 
    y => [y0, y1), [y1, y2), ... , [yN-1, y),
    all same sized intervals. 
    '''
    assert y >= size

    parts = list(F.pairwise(factorseq(y + size, size)))
    return parts if parts else [(0, y)]
