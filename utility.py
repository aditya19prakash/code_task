# utility.py

from passlib.context import CryptContext

# Set up the context for password hashing
# We specify the hashing algorithm (bcrypt) and schemes
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    """Hashes a plain-text password."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    """Verifies a plain password against its hashed version."""
    return pwd_context.verify(plain_password, hashed_password)