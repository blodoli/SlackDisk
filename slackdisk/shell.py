import subprocess

def runCmd(cmd):
    """Run a command and get standard output"""
    cmdArgs = cmd.split(' ')
    out = subprocess.Popen([cmd], 
            shell=True,
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE)
    stdout,stderr = out.communicate()
    return stdout.decode('utf-8').rstrip(), stderr.decode('utf-8').rstrip() 