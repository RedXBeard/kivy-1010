import os
from subprocess import Popen, PIPE
from kivy.storage.jsonstore import JsonStore


def run_syscall(cmd):
    """
    run_syscall; handle sys calls this function used as shortcut.
    ::cmd: String, shell command is expected.
    """
    p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = p.communicate()
    return out.rstrip()


PATH_SEPERATOR = '/'
if os.path.realpath(__file__).find('\\') != -1:
    PATH_SEPERATOR = '\\'

PROJECT_PATH = PATH_SEPERATOR.join(os.path.realpath(__file__).split(PATH_SEPERATOR)[:-1])

if PATH_SEPERATOR == '/':
    cmd = "echo $HOME"
else:
    cmd = "echo %USERPROFILE%"

out = run_syscall(cmd)
REPOFILE = "%(out)s%(ps)s.kivy-1010%(ps)skivy1010" % {'out': out.rstrip(), 'ps': PATH_SEPERATOR}

DB = JsonStore(REPOFILE)
directory = os.path.dirname(REPOFILE)
if not os.path.exists(directory):
    os.makedirs(directory)
if not DB.store_exists('high_score'):
    DB.store_put('high_score', 0)
DB.store_sync()