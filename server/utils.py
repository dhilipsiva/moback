import hmac
import hashlib
import string
import urllib

BASE62_ALPHABET = string.digits + string.ascii_letters
BASE92_ALPHABET = \
    BASE62_ALPHABET + '~!@#$%^&*()_-+={}[];"\'<>,.?/|\\'


def base92_encode(num):
    base92 = []
    alpha_len = len(BASE92_ALPHABET)
    while num != 0:
        num, i = divmod(num, alpha_len)
        base92.append(BASE92_ALPHABET[i])
    return ''.join(base92)


def hmac_sign(key, message):
    h = hmac.new(key, message, hashlib.sha224)
    base92_digest = base92_encode(int(h.hexdigest(), 16))
    return base92_digest


def make_query(base_path, param_dict):
    return(base_path + '?' + urllib.urlencode(param_dict))
