#!/usr/bin/env python3

from os import path
from cmd2 import style
import pprint
from . import shell, encoder

class Filetree():
    def __init__(self):
        # TODO: load filetree dinamically from slack space
        self.__filetree = {}
        self.__pwd_value = '/'
        self.__currentdir = self.__filetree
        self.encoder = encoder.Encoder()

    def print(self):
        """Prints file tree dictionary."""
        pprint.PrettyPrinter(width=1)
        pprint.pprint(self.__filetree)

    def pwd(self):
        """Returns current directory."""
        return self.__pwd_value

    def ls(self):
        """Returns current directory listing."""
        entries = sorted(self.__currentdir.keys())
        listing = ""
        for entry in entries:
            if entry.endswith('d'):
                listing = listing + style(f'{entry[:-1]}\t', fg='cyan')
            else:
                listing = listing + style(f'{entry[:-1]}\t', fg='white')
        return listing

    def cd(self, dir):
        """Changes current directory."""
        new_pwd = path.normpath(path.join(self.__pwd_value, dir))
        valid, new_dir = self.__isValidDir(new_pwd)
        if valid:
            self.__pwd_value = new_pwd
            self.__currentdir = new_dir
            return ''
        else:
            return "Directory doesn't exist"

    def mkdir(self, dir):
        """Create a new directory"""
        if dir == '':
            return ''
        new_pwd = path.normpath(path.join(self.__pwd_value, dir, '..'))
        valid, new_dir = self.__isValidDir(new_pwd)
        dirname = dir.split('/')[-1]
        if valid:
            if f'{dirname}d' in new_dir:
                return 'Directory exists'
            
            if f'{dirname}f' in new_dir:
                return 'File exists'
            
            new_dir[f'{dirname}d'] = {} 
            return ''
        else:
            return 'Invalid path'

    def rmdir(self, dir):
        """Remove a directory"""
        if dir == '':
            return ''
        new_pwd = path.normpath(path.join(self.__pwd_value, dir, '..'))
        valid, new_dir = self.__isValidDir(new_pwd)
        dirname = dir.split('/')[-1]
        if valid:
            if f'{dirname}d' not in new_dir:
                return 'Directory does not exist'
            
            if len(new_dir[f'{dirname}d']) == 0:
                del new_dir[f'{dirname}d']
            else:
                return 'This directory is not empty'

            return ''
        else:
            return 'Invalid path'

    def putStr(self, content, filepath):
        """Write a sting to a file"""
        new_pwd = path.normpath(path.join(self.__pwd_value, filepath, '..'))
        valid, new_dir = self.__isValidDir(new_pwd)
        filename = filepath.split('/')[-1]
        if valid:
            if f'{filename}f' not in new_dir:
                new_dir[f'{filename}f'] = content.encode('utf-8')
                return ''
            else:
                # TODO: treat overwrite
                return 'File already exists'
        else:
            return 'Invalid path'

    def putFile(self, real_filepath, virtual_filepath):
        """Add a file to the current directory of filetree"""
        # TODO: check if file exists (disk)
        new_pwd = path.normpath(path.join(self.__pwd_value, virtual_filepath, '..'))
        valid, new_dir = self.__isValidDir(new_pwd)
        filename = virtual_filepath.split('/')[-1]
        if valid:
            if f'{filename}f' not in new_dir:
                with open(real_filepath, 'rb') as f:
                    content = f.read()
                new_dir[f'{filename}f'] = content
                return ''
            else:
                # TODO: treat overwrite
                return 'File already exists'
        else:
            return 'Invalid path'

    def catFile(self, filepath):
        """Returns the content of a file"""
        new_pwd = path.normpath(path.join(self.__pwd_value, filepath, '..'))
        valid, new_dir = self.__isValidDir(new_pwd)
        filename = filepath.split('/')[-1]
        if valid:
            if f'{filename}f' not in new_dir:
                return 'File does not exist'
            try:
                return new_dir[f'{filename}f'].decode()
            except:
                return new_dir[f'{filename}f']
        else:
            return 'Invalid path'

    def rmFile(self, filepath):
        """Removes a file"""
        new_pwd = path.normpath(path.join(self.__pwd_value, filepath, '..'))
        valid, new_dir = self.__isValidDir(new_pwd)
        filename = filepath.split('/')[-1]
        if valid:
            if f'{filename}f' not in new_dir:
                return 'File does not exist'
            del new_dir[f'{filename}f']
            return ''
        else:
            return 'Invalid path'

    def getFile(self, filepath, real_filepath):
        """Saves a file to disk"""
        new_pwd = path.normpath(path.join(self.__pwd_value, filepath, '..'))
        valid, new_dir = self.__isValidDir(new_pwd)
        filename = filepath.split('/')[-1]
        if valid:
            if f'{filename}f' not in new_dir:
                return 'File does not exist'
            with open(real_filepath, 'wb') as f:
                f.write(new_dir[f'{filename}f'])
            return ''
        else:
            return 'Invalid path'

    def encodeFiletree(self, password):
        encodedTree = self.encoder.encodeTree(self.__filetree, password)
        return encodedTree

    def loadFileTree(self, encoded, password):
        decoded = self.encoder.decodeTree(str(encoded), password)
        self.__filetree = decoded.copy()
        self.__currentdir = self.__filetree

# Private methods

    def __isValidDir(self, dir):
        dirs = list(map(lambda x: x+'d', dir.split('/')))[1:]
        new_dir = self.__filetree
        if dir == '/':
            return (True, new_dir)
        for d in dirs:
            if d in new_dir:
                new_dir = new_dir[d]
            else:
                return (False, {})
        return (True, new_dir)

    def __getFileFromPath(self, filepath):
        dir = path.normpath(path.join(self.__pwd_value, dir, '..'))
        dirs = list(map(lambda x: x+'d', dir.split('/')))[1:]
        new_dir = self.__filetree
