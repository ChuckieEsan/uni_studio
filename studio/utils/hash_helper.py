import hashlib


def hash_password(s: str) -> str:
    return s


def md5(s: str) -> str:
    return hashlib.md5(s.encode(encoding='UTF-8')).hexdigest()
