'''
These are some tools that are used to configure the server.
'''
from random import choice
import string


def _genScrap(length=8, chars=string.letters + string.digits):
    return ''.join([choice(chars) for i in range(length)])


def genRandPasswd():
    '''
    Generate a random password
    '''
    return (_genScrap(10, string.digits) +
            _genScrap(10, string.ascii_letters))
