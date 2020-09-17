import socket
import sys
import funcy as F

from utils import etc_utils as etc

def DESCRIPTION(WHAT, WHY, KNOWN_ERROR=None):
    return {'DESCRIPTION': {'WHAT': WHAT,
                            'WHY': WHY,
                            'KNOWN_ERROR': KNOWN_ERROR}}
def CREATION():
    return {'CREATION': {'HOST_NAME': socket.gethostname(),
                         'COMMAND': ' '.join(sys.argv),
                         'GIT_HASH': etc.git_hash()}}

def data(DATA_SOURCES, HOW_TO_GEN, # Means meta.data
         WHAT, WHY, KNOWN_ERROR=None):
    return F.merge({'DATA_SOURCES': DATA_SOURCES},
                   DESCRIPTION(WHAT, WHY, KNOWN_ERROR),
                   CREATION(),
                   {'HOW_TO_GEN': HOW_TO_GEN})
