#!/usr/bin/env python3

import pickle
import zlib
import base64
from . import encrypter
class Encoder():
    def __init__(self):
        """Encoder class constructor"""

    def base64decode(self, data):
        """Decode a base 64 string"""
        return base64.b64decode(data)

    def base64encode(self, data):
        """Encode a string with base 64"""
        return base64.b64encode(data)

    def encrypt(self, data, key):
        """Encrypt a string using AES"""
        return encrypter.encrypt(key, data)

    def decrypt(self, data, key):
        """Decrypt a string using AES"""
        return encrypter.decrypt(key, data)

    def compress(self, data):
        """Compress a string using gzip"""
        compressed = zlib.compress(data, level=9)
        return(compressed)
    
    def decompress(self, data):
        """Decompress a string using gzip"""
        decompressed = zlib.decompress(data)
        return decompressed

    def encode(self, data, key):
        """Compress and encrypt a string, returning it encoded using base64"""
        try:
            databyte = data.encode()
        except:
            databyte = data
        finally:
            encoded = base64.b64encode(self.encrypt(self.compress(databyte), key))
            print(f"Original size {len(data)}")
            print(f"Encoded size {len(encoded)}")
            return encoded.decode('ascii')

    def decode(self, data, key):
        """Decrypt and decompress a base64 encoded string"""
        return self.decompress(self.decrypt(base64.b64decode(data), key))

    def encodeTree(self, tree, key):
        """Encode a python dictionary object"""
        return self.encode(pickle.dumps(tree), key)

    def decodeTree(self, encoded, key):
        """Decode a encoded python dictionary object"""
        decoded = self.decode(encoded, key)
        return pickle.loads(decoded)
