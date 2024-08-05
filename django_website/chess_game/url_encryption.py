
from .constants import ENCRYPTION_CHARS, ENCRYPTION_KEY


def encrypt(text):
    encrypted = ""

    for letter in text:
        index = ENCRYPTION_CHARS.index(letter)
        encrypted += ENCRYPTION_KEY[index]

    return encrypted

def decrypt(encrypted):
    decrypted = ""

    for letter in encrypted:
        index = ENCRYPTION_KEY.index(letter)
        decrypted += ENCRYPTION_CHARS[index]

    return decrypted