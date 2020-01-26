#!/usr/bin/env python3

from . import console

__all__ = ["console", "bmap", "filetree", "shell", "encoder", "encrypter"]

def init():
    console.new()

if __name__ == "__main__":
    init()