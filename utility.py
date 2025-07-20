# utility.py

from passlib.hash import pbkdf2_sha256

def hash_password(password):
    """Hashes a password for storing securely."""
    return pbkdf2_sha256.hash(password)

def verify_password(stored_hash, provided_password):
    """Verifies a stored password hash against one provided by the user."""
    return pbkdf2_sha256.verify(provided_password, stored_hash)