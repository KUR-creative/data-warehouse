from collections import namedtuple
import funcy as F
import itertools as I

#---------------------------------------------------------------
tup = lambda f: lambda argtup: f(*argtup)
go = lambda x,*fs: F.rcompose(*fs)(x)
pipe = F.rcompose

def inc(x): return x + 1
def dec(x): return x - 1

def plus(*xs):
    if not xs:
        return 0
    ret = xs[0]
    for x in xs[1:]:
        ret = ret + x
    return ret

def equal(*xs):
    if len(xs) == 1:
        return lambda *ys: equal(xs[0], *ys)
    else:
        for a,b in F.pairwise(xs):
            if a != b:
                return False
        return True

#--------------------------------------------------------------
def identity(x): return x

from funcy import all_fn # name from funcy
def every_pred(*ps): # name from clojure
    return F.all_fn(*ps)

#---------------------------------------------------------------
def is_empty(coll):
    return (not coll)

def take(n, seq=None):
    return F.take(n,seq) if not is_empty(seq) \
    else lambda xs: F.take(n,xs)

import random
def inplace_shuffled(li):
    random.shuffle(li)
    return li

def lzip(*seqs):
    return list(zip(*seqs))
def unzip(seq):
    return zip(*seq)

#--------------------------------------------------------------
# Curried functions
def map(f,*seq):
    return F.map(f,*seq) if not is_empty(seq) \
    else lambda *xs: F.map(f,*xs)
def lmap(f,*seq):
    return F.lmap(f,*seq) if not is_empty(seq) \
    else lambda *xs: F.lmap(f,*xs)
def tmap(f,*seq):
    return tuple(F.map(f,*seq)) if not is_empty(seq) \
    else lambda *xs: tuple(F.map(f,*xs))

def filter(f,*seq):
    return F.filter(f,*seq) if not is_empty(seq) \
    else lambda *xs: F.filter(f,*xs)
def lfilter(f,*seq):
    return F.lfilter(f,*seq) if not is_empty(seq) \
    else lambda *xs: F.lfilter(f,*xs)
def tfilter(f,*seq):
    return tuple(F.filter(f,*seq)) if not is_empty(seq) \
    else lambda *xs: tuple(F.filter(f,*xs))

def remove(f,*seq):
    return F.remove(f,*seq) if not is_empty(seq) \
    else lambda *xs: F.remove(f,*xs)
def lremove(f,*seq):
    return F.lremove(f,*seq) if not is_empty(seq) \
    else lambda *xs: F.lremove(f,*xs)
def tremove(f,*seq):
    return tuple(F.remove(f,*seq)) if not is_empty(seq) \
    else lambda *xs: tuple(F.remove(f,*xs))

def starmap(f,*seq):
    return I.starmap(f,*seq) if not is_empty(seq) \
    else lambda *xs: I.starmap(f,*xs)
def lstarmap(f,*seq):
    return list(I.starmap(f,*seq)) if not is_empty(seq) \
    else lambda *xs: list(I.starmap(f,*xs))
def tstarmap(f,*seq):
    return tuple(I.starmap(f,*seq)) if not is_empty(seq) \
    else lambda *xs: tuple(I.starmap(f,*xs))

def mapcat(f,*seq):
    return F.mapcat(f,*seq) if not is_empty(seq) \
    else lambda *xs: F.mapcat(f,*xs)
def lmapcat(f,*seq):
    return F.lmapcat(f,*seq) if not is_empty(seq) \
    else lambda *xs: F.lmapcat(f,*xs)
def tmapcat(f,*seq):
    return tuple(F.mapcat(f,*seq)) if not is_empty(seq) \
    else lambda *xs: tuple(F.mapcat(f,*xs))

def group_by(f, seq=None):
    return F.group_by(f, seq) if not is_empty(seq)\
    else lambda xs: F.group_by(f, xs)

def walk(f,*seq):
    return F.walk(f,*seq) if not is_empty(seq) \
    else lambda *xs: F.walk(f,*xs)

def walk_values(f, coll=None):
    return F.walk_values(f, coll) if not is_empty(coll) \
    else lambda coll: F.walk_values(f, coll)

def walk_keys(f, coll=None):
    return F.walk_keys(f, coll) if not is_empty(coll) \
    else lambda coll: F.walk_keys(f, coll)

#---------------------------------------------------------------
from funcy import repeat, repeatedly
def lrepeatedly(f, n): # infinite list not allowed.
    return list(F.repeatedly(f, n))

from funcy import cat, lcat
from funcy import concat, lconcat
from funcy import flatten, lflatten

#---------------------------------------------------------------
def split_with(sep_idxs, li):
    ''' 
    If sep_idxs is empty, then it returns empty generator. 
    But I don't know why..
    '''
    for s,t in F.pairwise( I.chain(sep_idxs, [len(li)]) ):
        yield li[s:t]
def lsplit_with(sep_idxs, li):
    return list(split_with(sep_idxs, li))
def tsplit_with(sep_idxs, li):
    return tuple(split_with(sep_idxs, li))

'''
def partition_with(nums_in_parts, seq):
    ret = []
    iseq = iter(seq)
    for n in nums_in_parts:
        ret.append( take(n,iseq) )
    return ret
'''

def foreach(f,*seq):
    F.lmap(f,*seq)
    return None

@F.autocurry
def cut_with_bound(pred, xs):
    chunk = []
    for x in xs:
        chunk.append(x)
        if pred(x):
            yield chunk
            chunk = []
    if chunk: #remaining elements
        yield chunk

#--------------------------------------------------------------
def dict2namedtuple(type_name, dic):
    return namedtuple(type_name, sorted(dic))(**dic)

#--------------------------------------------------------------
def is_public_name(name):
    return not name.startswith('__')
def attr_names(obj, pred=lambda n: True):
    return tuple(n for n in dir(obj) if pred(n))
def attrs(obj, get=dir):
    return tuple(getattr(obj, name) for name in get(obj))

def pub_attr_names(obj):
    return attr_names(obj, is_public_name)
def pub_attrs(obj):
    return attrs(obj, pub_attr_names)

def prop(p, obj=None):
    return(getattr(obj, p) if (isinstance(obj,tuple) and 
                               isinstance(p,str))
      else obj[p] if hasattr(obj,'__getitem__')
      else getattr(obj, p) if obj 
      else lambda o: prop(p,o))

