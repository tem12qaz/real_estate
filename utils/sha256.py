import hashlib


def sha256(string: str) -> str:
    h = hashlib.new('sha256')
    h.update(bytes(string, encoding='utf8'))
    return h.hexdigest()
