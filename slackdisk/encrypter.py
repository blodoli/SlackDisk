import binascii
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto import Random
from Crypto.Protocol.KDF import PBKDF2

key_bytes = 32   # AES256

# Choose a random, 16-byte IV.
# iv = Random.new().read(AES.block_size)

# Randomly generated salt and iv
iv = bytes.fromhex("6dbc100320476d4fc752289b136ba62b")
salt = b"378597a6c7ff3a099fbf4803624ee3051acdbf40"

def encryptAES(key, iv, plaintext):
    "Encrypt using a 32 bit key and a 16 bit IV"
    assert len(key) == key_bytes

    # Convert the IV to a Python integer.
    iv_int = int(binascii.hexlify(iv), 16) 

    # Create a new Counter object with IV = iv_int.
    ctr = Counter.new(AES.block_size * 8, initial_value=iv_int)

    # Create AES-CTR cipher.
    aes = AES.new(key, AES.MODE_CTR, counter=ctr)

    # Encrypt and return IV and ciphertext.
    ciphertext = aes.encrypt(plaintext)
    return (iv, ciphertext)

def decryptAES(key, iv, ciphertext):
    "Decrypt using a 32 bit key and a 16 bit IV"
    assert len(key) == key_bytes

    # Initialize counter for decryption. iv should be the same as the output of
    # encrypt().
    iv_int = int(binascii.hexlify(iv), 16) 
    ctr = Counter.new(AES.block_size * 8, initial_value=iv_int)

    # Create AES-CTR cipher.
    aes = AES.new(key, AES.MODE_CTR, counter=ctr)

    # Decrypt and return the plaintext.
    plaintext = aes.decrypt(ciphertext)
    return plaintext

def encrypt(password, plaintext):
    "Encrypt using a password string"
    key = PBKDF2(password, salt, key_bytes)
    (iv_, ciphertext) = encryptAES(key, iv, plaintext)
    return ciphertext

def decrypt(password, ciphertext):
    "Decrypt using a password string"
    key = PBKDF2(password, salt, key_bytes)
    plaintext = decryptAES(key, iv, ciphertext)
    return plaintext

