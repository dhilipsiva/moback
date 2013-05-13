import hmac
import hashlib
import string

BASE62_ALPHABET = string.digits + string.ascii_letters
BASE92_ALPHABET = BASE62_ALPHABET + '~!@#$%^&*()_-+={}[];"\'<>,.?/|\\'


def base92_encode(num):
    '''
    Warning: This operation is not invertible (yet!)
    '''
    base92 = []
    alpha_len = len(BASE92_ALPHABET)
    while num != 0:
        num, i = divmod(num, alpha_len)
        base92.append(BASE92_ALPHABET[i])
    return ''.join(base92)  # WARNING: Numbers are in reverse order


def hmac_sign(key, message):
    h = hmac.new(key, message, hashlib.sha224)
    base92_digest = base92_encode(int(h.hexdigest(), 16))
    return base92_digest


def hmac_verify(key, message):
    signature_len = message[:2].strip()
    if not signature_len:
        return False, None
    try:
        signature_len = int(signature_len, 16)
    except ValueError:
        return False, None
    msg = message[2:-signature_len]
    signature = message[-signature_len:]
    if len(signature) != signature_len:
        return False, None
    h = hmac.new(key, msg, hashlib.sha224)
    base92_hd = base92_encode(int(h.hexdigest(), 16))
    if len(base92_hd) != len(signature):
        return False, None
    r = True
    for a, b in zip(base92_hd, signature):
        if a != b:
            r = False
    return r, msg
