import hashlib
from base64 import b64decode
#from werkzeug.security import pbkdf2_bin


def check_login_credentials(user, password):
    if not user:
        return
    return check_hash(password, user.password)


def check_hash(password, hash_):
    """Check a password against an existing hash."""
    if isinstance(password, str):
        password = password.encode('utf-8')
    algorithm, hash_function, cost_factor, salt, hash_a = hash_.split('$')
    assert algorithm == 'PBKDF2'
    salt = salt.encode('utf-8')
    hash_a = b64decode(hash_a)
    hash_b = pbkdf2_bin(password, salt, int(cost_factor), len(hash_a),
                        getattr(hashlib, hash_function))
    # Same as "return hash_a == hash_b" but takes a constant time.
    # See http://carlos.bueno.org/2011/10/timing.html
    assert len(hash_a) == len(hash_b)
    diff = 0
    for char_a, char_b in zip(hash_a, hash_b):
        diff |= char_a ^ char_b
    return diff == 0
