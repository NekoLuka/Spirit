import hashlib, uuid

def saltPassword(password: str) -> str:
    salt = uuid.uuid4().hex
    saltedHash = hashlib.sha256(salt.encode() + password.encode()).hexdigest()[32:]
    return salt + saltedHash

def checkPassword(password: str, hash: str) -> bool:
    salt = hash[:32]
    saltedHash = hashlib.sha256(salt.encode() + password.encode()).hexdigest()[32:]
    return salt + saltedHash == hash