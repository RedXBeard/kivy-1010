import os
from subprocess import Popen, PIPE

from kivy.storage.jsonstore import JsonStore
from kivy.utils import get_color_from_hex


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
if not DB.store_exists('theme'):
    DB.store_put('theme', 'light')
if not DB.store_exists('sound'):
    DB.store_put('sound', True)
DB.store_sync()

THEME = {'dark': {'background': get_color_from_hex('303030'),
                  'labels': get_color_from_hex('666666')},
         'light': {'background': get_color_from_hex('F0F0F0'),
                   'labels': get_color_from_hex('E2DDD5')}}

SOUNDS = {'placed': {'path': 'assets/sounds/placed.wav', 'volume': .8, 'priority': 2},
                   'missed_placed': {'path': 'assets/sounds/missed_placed.wav', 'volume': .4, 'priority': 4},
                   'line_clear': {'path': 'assets/sounds/line_clear.wav', 'volume': .2, 'priority': 1},
                   'new_shapes': {'path': 'assets/sounds/new_shapes.wav', 'volume': .5, 'priority': 3},
                   'game_on': {'path': 'assets/sounds/game_on.wav', 'volume': .3, 'priority': 0}}

COLOR = [get_color_from_hex('DC6555'),  # red
                get_color_from_hex('5BBEE5'),  # light blue
                get_color_from_hex('448FC4'),
                get_color_from_hex('6FE5FE'),
                get_color_from_hex('50B5D5'),
                get_color_from_hex('EC9449'),  # orange1
                get_color_from_hex('ED954A'),  # orange2
                get_color_from_hex('FFC658'),
                get_color_from_hex('E57D4F'),
                get_color_from_hex('C25041'),
                get_color_from_hex('FF8271'),
                get_color_from_hex('FAC73D'),  # yellow1
                get_color_from_hex('FFC63E'),  # yellow2
                get_color_from_hex('97DB55'),  # green1
                get_color_from_hex('4DD5B0'),  # green2
                get_color_from_hex('98DC55'),  # green3
                get_color_from_hex('59CB86'),  # green4
                get_color_from_hex('5AC986'),  # dark green
                get_color_from_hex('7B8ED4'),  # purple1
                get_color_from_hex('7E8ED5'),  # purple2
                get_color_from_hex('E86981')]  # pink

SHAPES = {'straight5': [dict(cols=5, rows=1, array=[1, 1, 1, 1, 1]),
                                      dict(cols=1, rows=5, array=[1, 1, 1, 1, 1])],
                  'straight4': [dict(cols=4, rows=1, array=[1, 1, 1, 1]),
                                      dict(cols=1, rows=4, array=[1, 1, 1, 1]),],
                  'straight3': [dict(cols=3, rows=1, array=[1, 1, 1]),
                                       dict(cols=1, rows=3, array=[1, 1, 1]),],
                  'straight2': [dict(cols=2, rows=1, array=[1, 1]),
                                      dict(cols=1, rows=2, array=[1, 1]),],
                  'straight1': [dict(cols=1, rows=1, array=[1]),],
                  'scube': [dict(cols=2, rows=2, array=[1, 1, 1, 1]),],
                  'bcube': [dict(cols=3, rows=3, array=[1, 1, 1,
                                                                               1, 1, 1,
                                                                               1, 1, 1]),],
                  'sL': [dict(cols=2, rows=2, array=[1, 1, 0, 1]),
                          dict(cols=2, rows=2, array=[1, 0, 1, 1]),
                          dict(cols=2, rows=2, array=[1, 1, 1, 0]),
                          dict(cols=2, rows=2, array=[0, 1, 1, 1]),],
                  'mL': [dict(cols=2, rows=3, array=[1, 0,
                                                                         1, 0,
                                                                         1, 1]),
                           dict(cols=2, rows=3, array=[1, 1,
                                                                         1, 0,
                                                                         1, 0]),
                           dict(cols=2, rows=3, array=[1, 1,
                                                                         0, 1,
                                                                         0, 1]),
                           dict(cols=2, rows=3, array=[0, 1,
                                                                         0, 1,
                                                                         1, 1]),
                           dict(cols=3, rows=2, array=[1, 1, 1,
                                                                         1, 0, 0]),
                           dict(cols=3, rows=2, array=[1, 1, 1,
                                                                         0, 0, 1]),
                           dict(cols=3, rows=2, array=[1, 0, 0,
                                                                         1, 1, 1]),
                           dict(cols=3, rows=2, array=[0, 0, 1,
                                                                         1, 1, 1]),],
                  'bL': [dict(cols=3, rows=3, array=[1, 1, 1,
                                                                         1, 0, 0,
                                                                         1, 0, 0]),
                          dict(cols=3, rows=3, array=[1, 1, 1,
                                                                        0, 0, 1,
                                                                        0, 0, 1]),
                          dict(cols=3, rows=3, array=[1, 0, 0,
                                                                        1, 0, 0,
                                                                        1, 1, 1]),
                          dict(cols=3, rows=3, array=[0, 0, 1,
                                                                        0, 0, 1,
                                                                        1, 1, 1]),]
                }
