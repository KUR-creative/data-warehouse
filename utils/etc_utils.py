''' 
Miscellaneous useful utility functions.
These functions could be used by copy & paste. To do so, 
a module import statement is close to the function it uses.
'''

def modulo_pad(m, x=None):
    ''' 2a = x + modulo_pad (mod m), where a < x < 2a '''
    return((m - (x % m)) % m if x is not None
      else lambda x: modulo_pad(x))

def factorseq(d, y=None):
    ''' Generate factor sequence: 0, d, 2d, ..., y - d '''
    if y is None:
        return lambda y: factorseq(d, y)
    else:
        assert y % d == 0
        def acc():
            beg = 0
            max = y
            while beg != max:
                yield beg
                beg += d
        return acc()
    # Note: When just use naive generator, it raises TypeError.
    #
    #ex) 
    # list(map(factorseq(4), [12,20,32]))
    # TypeError: 'generator' object is not callable
    #
    # So I wrapped it up with inner funtion.
    
def factors(d, y=None): # for memoization
    return list(factorseq(d,y))
        
import funcy as F
def partition(y, size):
    ''' 
    y => [y0, y1), [y1, y2), ... , [yN-1, y),
    all same sized intervals. 
    '''
    assert y >= size

    parts = list(F.pairwise(factorseq(y + size, size)))
    return parts if parts else [(0, y)]

#--------------------------------------------------------------
import random
def inplace_shuffled(li):
    random.shuffle(li)
    return li

#--------------------------------------------------------------
from typing import Iterable, Any
def sjoin(s, iterable: Iterable[Any]):
    return s.join(map(str, iterable))
