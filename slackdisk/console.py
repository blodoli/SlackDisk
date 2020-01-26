#!/usr/bin/env python3

import cmd2
from cmd2 import style
from . import bmap, filetree, encoder

class Console(cmd2.Cmd):
    def __init__(self):
        super().__init__(multiline_commands=[], persistent_history_file='~/.slackdisk')
        del cmd2.Cmd.do_py
        del cmd2.Cmd.do_run_script
        del cmd2.Cmd.do_run_pyscript
        del cmd2.Cmd.do_shortcuts
        del cmd2.Cmd.do_macro
        del cmd2.Cmd.do_alias
        
        self.usabledirs = '/bin /etc /home /lib /lib32 /lib64 /opt /root'
        self.initialfile = '/bin/bash'
        self.password = 'slackdisk'
        self.tree = filetree.Filetree() 
        self.bmap = bmap.Bmap()
        self.encoder = encoder.Encoder()
        self.statement_parser.aliases = {
            'exit': 'quit',
            'q': 'quit',
            'h': 'help'
            }
        self.minimaltime = '100' # days
        self.prompt = style("slack> ", fg='blue')
        self.settable['usabledirs'] = "Directories to save hidden file system, separated by spaces."
        self.settable['minimaltime'] = "Minimal time (in days) that the file must not have been modified"
        self.settable['password'] = "Password used to encrypt the file system on slack space"
        self.settable['initialfile'] = "File to save (or load) the beginning of the file system on slack space"
        self.intro = style(r"""
   _____ _            _    _____  _     _    
  / ____| |          | |  |  __ \(_)   | |   
 | (___ | | __ _  ___| | _| |  | |_ ___| | __
  \___ \| |/ _` |/ __| |/ / |  | | / __| |/ /
  ____) | | (_| | (__|   <| |__| | \__ \   < 
 |_____/|_|\__,_|\___|_|\_\_____/|_|___/_|\_\ v0.1
                                             """, fg='yellow', bold=True)

    def do_banner(self, args):
        """Prints the banner of the program"""
        self.poutput(self.intro)
    
    def do_ls(self, args):
        """Lists the current directory"""
        self.poutput(self.tree.ls())

    def do_cd(self,dir):
        """Changes current directory"""
        self.poutput(self.tree.cd(dir))
        
    def do_pwd(self,args):
        """Prints the current directory"""
        self.poutput(self.tree.pwd())

    def do_mkdir(self,args):
        """Creates a directory"""
        self.poutput(self.tree.mkdir(args))

    def do_rmdir(self,args):
        """Removes a directory"""
        self.poutput(self.tree.rmdir(args))

    def do_putstr(self, args):
        """Function to save string to file."""
        args = args.arg_list
        if len(args) != 2:
            self.poutput('Usage: putstr <string to put on file> <file path on hidden file system>')
        else:
            content = args[0]
            name = args[1]
            self.poutput(self.tree.putStr(content, name))

    def do_put(self, args):
        """
        Puts a file on the current directory
        Usage: put <file path on disk> <file path on hidden file system>
        """
        args = args.arg_list
        if len(args) != 2:
            self.poutput('Usage: put <file path on disk> <file path on hidden file system>')
        else:
            filepath = args[0]
            name = args[1]
            self.poutput(self.tree.putFile(filepath, name))

    def do_get(self, args):
        """
        Gets a file from the current directory
        Usage: get <file path on hidden file system> <file path on disk>
        """
        args = args.arg_list
        if len(args) != 2:
            self.poutput('Usage: Usage: get <file path on hidden file system> <file path on disk>')
        else:
            name = args[0]
            filepath = args[1]
            self.poutput(self.tree.getFile(name, filepath))

    def do_cat(self,file):
        """Prints a file content on screen"""
        self.poutput(self.tree.catFile(file))

    def do_rm(self,file):
        """Removes a file"""
        self.poutput(self.tree.rmFile(file))

    def do_total(self, args):
        """Gets available slack space in the usable directories (total)"""
        self.poutput(self.bmap.total(self.usabledirs, self.minimaltime))

    def do_bmap(self, args):
        """Using bmap's functions. Type bmap help to get command help."""
        args = args.arg_list
        mode = args[0]
        if mode == 'help':
            """Prints help of this command"""
            self.poutput(self.bmap.help())
        elif mode == 'put':
            """Saves string to file"""
            file = args[1]
            data_str = ' '.join(args[2:])
            self.poutput(self.bmap.put(file, data_str))
        elif mode == 'get':
            """Gets string from file"""
            file = args[1]
            self.poutput(self.bmap.get(file))
        elif mode == 'clean':
            """Wipes the slack space of a file"""  
            file = args[1]
            self.poutput(self.bmap.wipe(file))
        else:
            self.poutput(self.bmap.help())
    
    def do_index(self, args):
        """Index disk"""
        self.poutput(self.bmap.indexDisk(self.usabledirs, self.minimaltime))

    def do_save(self, args):
        """Save current file system to slack space"""
        encoded = self.tree.encodeFiletree(self.password)
        self.bmap.save(encoded, self.initialfile)

    def do_load(self, args):
        """Load file system from slack space"""
        encoded = self.bmap.load(self.initialfile)
        self.tree.loadFileTree(encoded, self.password)

    def do_savestring(self, data):
        """Save arbitrary string to slack space"""
        self.bmap.save(data, self.initialfile)

    def do_loadstring(self, args):
        """Load arbitrary string to from slack space"""
        loaded = self.bmap.load(self.initialfile)
        self.poutput(loaded)

    def do_encode(self, args):
        """Encode file tree"""
        encoded = self.tree.encodeFiletree(self.password)

    def do_decode(self, data):
        """Decode file tree"""
        self.tree.loadFileTree(data, self.password)

    def do_print(self, args):
        """Print file tree"""
        self.tree.print()
        
    def do_quit(self, arg):
        """Exits the application"""
        print("Bye")
        return True

    def _onchange_minimaltime(self, old, new):
        """Hook to be called when minimal time is changed"""
        # TODO: redo indexing
        print(old, new)

def new():
    app = Console()
    app.cmdloop()