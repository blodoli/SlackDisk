#!/usr/bin/env python3

from . import shell
import re

helpStr = """
    Usage: bmap [MODE] [FILE] [ARGUMENTS]
    Modes available:
        get:\tGets content of slack space of a file
        put:\tPuts content on slack space of a file
        clean:\tWipes contents of slack space of a file
"""

class Bmap():
    def __init__(self):
        self.__disk_index = {}
        self.__priority_list = []
        self.__total_size = 0
        self.minimaltime = 100
        self.usabledirs = '/bin /etc /home /lib /lib32 /lib64 /opt /root'

    def put(self, filename, data_str):
        """Puts a string on the slack space of a file"""
        # TODO: prevent overwrite
        stdout, stderr = shell.runCmd(f"echo {data_str} | bmap --mode putslack '{filename}'")
        return stdout

    def get(self, filename):
        """Gets a string from the slack space of a file"""
        stdout, stderr = shell.runCmd(f"bmap --mode slack '{filename}'")
        return stdout

    def getSlackSpace(self, filename):
        """Gets slack space available on given file"""
        # TODO: test
        stdout, stderr = shell.runCmd(f"bmap --mode slack '{filename}'") 
        if (stdout and len(stdout) > 12):
            slack_space = int(re.search(r'slack size: (\d+)', stderr).groups()[0])
            return slack_space
        else:
            return 0

    def wipe(self, filename):
        """Wipes the slack space of a file"""
        stdout, stderr = shell.runCmd(f"bmap --mode wipe '{filename}'")
        return stdout

    def total(self, usable, days):
        """Gets available slack space on usable dirs that have not been changed in a certain amount of days (total)"""
        if (self.__total_size == 0):
            self.indexDisk(usable, days)
        return f'{self.bytes_to_human(self.__total_size)} in {len(self.__priority_list)} files'

    def help(self):
        """Returns bmap's help"""
        return helpStr

    def indexDisk(self, usable, days):
        """Indexes whole disk by inode.
        Indexed info:
            filename
            modification date
            slack space
        """
        print("Indexing usable directories")
        index = {}
        free = 0
        if days != '0':
            stdout, stderr = shell.runCmd(f"find {usable} -mtime +{days} -type f")
        else:
            stdout, stderr = shell.runCmd(f"find {usable} -type f")
        files = stdout.split('\n')
        for file in files:
            stdout, stderr = shell.runCmd(f"stat -c '%i %Y' {file}") 
            if (len(stdout) > 0):
                inode = stdout.split(' ')[0] 
                mod_date = stdout.split(' ')[1] 
            slack_space = self.getSlackSpace(file)
            if(slack_space > 10):
                free = free + slack_space
                index[inode] = {}
                index[inode]['filename'] = file
                index[inode]['mod_date'] = mod_date
                index[inode]['slack'] = slack_space
        self.__disk_index = index
        self.__priority_list = sorted(index.keys(), key=lambda x: (index[x]['mod_date'], -index[x]['slack']))
        self.__total_size = free
        return "Indexing done!"

    def save(self, encodedString, initialFile):
        """Saves a arbitrary string on slack space"""
        if len(self.__disk_index.keys()) == 0:
            self.indexDisk(self.usabledirs, self.minimaltime)
        remaining = encodedString
        currentFile = initialFile
        nextIndex = 0
        while len(remaining) != 0:
            space = self.getSlackSpace(currentFile) 
            if len(remaining) < space:
                slackPartial = f':{remaining}'
                remaining = ''
                nextFile = ''
            else:
                if nextIndex > len(self.__priority_list):
                    # TODO: treat exception
                    return
                nextInode = self.__priority_list[nextIndex]
                nextFile = self.__disk_index[nextInode]["filename"]
                nextIndex = nextIndex + 1
                if nextFile == initialFile:
                    nextInode = self.__priority_list[nextIndex]
                    nextFile = self.__disk_index[nextInode]["filename"]
                    nextIndex = nextIndex + 1
                space = space - len(str(nextInode)) - 1
                slackPartial = f'{str(nextInode)}:{remaining[:space]}'
                remaining = remaining[space:]
            self.wipe(currentFile)
            self.put(currentFile, slackPartial)
            currentFile = nextFile

    def load(self, initialFile):
        """Loads a arbitrary string from slack space"""
        if len(self.__disk_index.keys()) == 0:
            self.indexDisk(self.usabledirs, self.minimaltime)
        slack = self.get(initialFile)
        nextInode = slack.split(':', 2)[0]
        encodedString = slack.split(':', 2)[1]
        while nextInode != '':
            nextFile = self.__disk_index[nextInode]['filename']
            slack = self.get(nextFile)
            nextInode = slack.split(':', 2)[0]
            encodedString = encodedString + slack.split(':', 2)[1]
        return encodedString

    def bytes_to_human(self, num, suffix='B'):
        for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
            if abs(num) < 1024.0:
                return "%3.1f%s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f%s%s" % (num, 'Yi', suffix)