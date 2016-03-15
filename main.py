import webbrowser
from datetime import datetime, timedelta
from random import choice
from urllib2 import urlopen, URLError

from kivy import platform
from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scatterlayout import ScatterLayout
from kivy.utils import get_color_from_hex

from config import DB, THEME, COLOR, SHAPES, SOUNDS, WIN_SIZE

__version__ = '1.5.2'

# SCORE calculation
"""
1 - 0 - 0 - 0*5
2 - 10 - 5 - 1*5
3 - 30 - 10 - 2*5
4 - 60 - 15 - 3*5
5 - 100 - 20 - 4*5
"""

SOUND = False


def get_ratio():
    return (Window.width < Window.height and
            float(Window.width) / float(Window.height) or
            float(Window.height) / float(Window.width))


def get_color(obj):
    u"""Color of widget returns.
    :param obj:
    """
    try:
        obj_color = filter(
            lambda x:
            str(x).find('Color') != -1, obj.canvas.before.children)[0]
    except IndexError:
        obj_color = None
    return obj_color


def set_color(obj, color):
    obj_color = get_color(obj)
    try:
        obj_color.rgba = color
    except AttributeError:
        pass


def shape_on_box(shape, label_index):
    """
    Find shapes probable positioned indexes on board
    via given specific label on board
    :param label_index:
    :param shape:
    """
    shape_box_on_board = []
    line_left = (label_index / 10) * 10
    if shape.cols <= (label_index - line_left + 1):
        for i in range(0, shape.rows):
            row = range(
                label_index + i * 10,
                (label_index + i * 10) - shape.cols, -1)
            row.reverse()
            shape_box_on_board.extend(row)
    return shape_box_on_board


def check_occupied(board, board_row, shape_objs, return_position=False):
    """
    Check if given possible position list which is
    generated/found with 'shape_on_box' method
    is already occupied with other shape or not
    :param return_position:
    :param shape_objs:
    :param board_row:
    :param board:
    """
    occupied = False
    positions = []
    if not board_row:
        occupied = True
    index = 0
    for i in board_row:
        board_label = board.children[i]
        shape_label = str(shape_objs[index]).find('Label') != -1
        if board_label.filled:
            if shape_label:
                occupied = True
                break
        else:
            if shape_label:
                positions.append(i)
        index += 1
    if return_position:
        return occupied, positions
    else:
        return occupied


def get_lines(indexes):
    """in row and in cols indexes are taken.
    :param indexes:
    """
    lines = []
    for i in indexes:
        tmp_cols = range(i % 10, 100, 10)
        tmp_rows = range((i / 10) * 10, (i / 10) * 10 + 10, 1)
        try:
            lines.index(tmp_cols)
        except ValueError:
            lines.append(tmp_cols)
        try:
            lines.index(tmp_rows)
        except ValueError:
            lines.append(tmp_rows)
    return lines


def free_positions(board, shape):
    """
    check for the given shape is there any
    suitable position is available or not on board
    :param shape:
    :param board:
    """
    pos_on_board = board.children
    place = False
    all_positions = []
    for pos in pos_on_board:
        label_index = board.children.index(pos)
        shape_objs = shape.children
        try:
            shape_box_on_board = shape_on_box(shape, label_index)
            occupied, positions = check_occupied(
                board, shape_box_on_board, shape_objs, return_position=True)
            if occupied:
                raise IndexError
            place = True or place
            all_positions.append(positions)
        except:
            pass
    return place, all_positions


def get_scoreboard_height():
    return Window.height / 10


def get_board_size():
    score_board_height = get_scoreboard_height()
    return float(min(Window.width - 80,
                     (Window.height - score_board_height) / 10 * 7))


def open_page(*args):
    webbrowser.open(args[1])


def generate_play_button():
    button = Button(background_color=get_color_from_hex('58CB85'))
    button.curve = 25
    button.image.source = 'assets/images/play.png'
    set_color(button, get_color_from_hex('58CB85'))
    return button


def generate_medal_label():
    """
    :return: Label
    """
    label = Label(size_hint=(.7, 1))
    label.curve = 25
    label.image.source = 'assets/images/award.png'
    label.image.size = ('50sp', '50sp')
    set_color(label, get_color_from_hex('5BBEE5'))
    return label


def sync_score(score):
    DB.store_put('score', score)
    DB.store_sync()


def sync_board(board):
    DB.store_put('board', board)
    DB.store_sync()


def get_synced_board():
    board = DB.store_get('board')
    return board


def get_synced_shapes():
    shapes = DB.store_get('shapes')
    return shapes


def get_record():
    try:
        high_score = DB.store_get('high_score')
    except KeyError:
        high_score = 0
    return high_score


class Shape(GridLayout):
    """
    Generate shapes from given already set list with random colour.
    """

    def __init__(
            self, rows=None, cols=None, array=None,
            color=None, color_set=COLOR):
        super(Shape, self).__init__()
        shape_key = choice(SHAPES.keys())
        # shape_key = "straight1"
        shape = choice(SHAPES[shape_key])
        # shape = SHAPES[shape_key][1]
        ccolor = choice(color_set)
        self.rows = rows and rows or shape['rows']
        self.cols = cols and cols or shape['cols']
        self.array = array and array or shape['array']
        self.color = color and color or ccolor

    def get_colors(self):
        """Return shape color"""
        result = []
        for child in self.children:
            if str(child).find('Label') != -1:
                result.append(get_color(child))
        return result

    def resize(self):
        try:
            label = self.children[0]
            self.size = (label.size[0] * self.rows,
                         label.size[1] * self.cols)
        except IndexError:
            pass


class CustomScatter(ScatterLayout):
    """Shape class"""
    wh_per = 25
    last_moved = None
    touch_distance = 0
    min_size = 0

    def __init__(self, *args, **kwargs):
        super(CustomScatter, self).__init__(*args, **kwargs)
        self.movement = 0

    def on_transform_with_touch(self, touch):
        """take action when shape touched.
        :param touch:
        """
        super(CustomScatter, self).on_transform_with_touch(touch)

        root = self.parent.parent
        root.last_moved = datetime.now()
        root.clear_free_place()
        wh = get_ratio()
        try:
            if self.do_translation_x and self.do_translation_y:
                shape = self.children[0].children[0]
                orig_height = (shape.rows * shape.children[0].size[0] +
                               shape.rows * shape.spacing[0])
                dust_height = orig_height - self.min_size if shape.rows < 5 else 0
                per_box = (((len(shape.children) * root.per_box) +
                            (len(shape.children) * 3)) -
                           (len(shape.children) *
                            (root.per_box - 5))) / len(shape.children)
                for label in shape.children:
                    label.size = (root.per_box - 5, root.per_box - 5)
                    label.curve = label.size[0] * wh / 3
                shape.spacing = (per_box, per_box)
                shape.resize()
                resized_height = (shape.rows * shape.children[0].size[0] +
                                  shape.rows * shape.spacing[0])

                if not self.touch_distance:
                    self.touch_distance = resized_height - orig_height + dust_height

        except IndexError:
            pass

    def on_bring_to_front(self, touch):
        super(CustomScatter, self).on_bring_to_front(touch)

    def on_touch_up(self, touch):
        super(CustomScatter, self).on_touch_up(touch)
        self.position_calculation()
        self.reset_shape()

    def on_touch_down(self, touch):
        super(CustomScatter, self).on_touch_down(touch)
        root = self.parent.parent
        posx_check = self.pos[0] < touch.pos[0] < self.pos[0] + self.width
        posy_check = self.pos[1] < touch.pos[1] < self.pos[1] + self.height
        if platform in ['android', 'ios'] and posx_check and posy_check:
            row_count = self.children[0].children[0].rows
            Animation(
                x=self.pos[0], y=(touch.pos[1] +
                                  (row_count > 1 and
                                   row_count or
                                   row_count + 1) *
                                  (3 + root.per_box)),
                t='linear', duration=.05).start(self)

    def reset_shape(self):
        try:
            wh = get_ratio()
            if self.do_translation_x and self.do_translation_y:
                shape = self.children[0].children[0]
                for label in shape.children:
                    label.size = (self.wh_per, self.wh_per)
                    label.curve = self.wh_per * wh / 3
                shape.spacing = (2, 2)
                shape.resize()
                self.touch_distance = 0
        except IndexError:
            pass

    def calculate_shape_size(self, width, height):
        self.wh_per = ((min(width, height) - 12) / 7)
        self.min_size = (self.wh_per + 2) * 5

    def position_calculation(self):
        """
        On board, taken scatter position is on a label or not check is handled
        """
        try:
            board = self.parent.parent.board
            labels = board.children
            obj_x, obj_y = self.pos
            shape = self.children[0].children[0]
            flag = False
            for label in labels:
                pos_x, pos_y = label.pos
                lbl_wid, lbl_hei = label.size
                pos_x_check = (
                    pos_x - lbl_wid / 2 <=
                    obj_x + self.movement <=
                    pos_x + lbl_wid / 2)
                pos_y_check = (
                    pos_y - lbl_hei / 2 <=
                    obj_y - self.touch_distance <=
                    pos_y + lbl_hei / 2)
                if pos_x_check and pos_y_check:
                    lbl_index = labels.index(label)
                    line_left = (lbl_index / 10) * 10
                    if shape.cols <= (lbl_index - line_left + 1):
                        self.get_colored_area(board, label)
                        flag = True
                        break
            if not flag:
                raise IndexError
        except AttributeError:
            pass
        except IndexError:
            if hasattr(self, 'pre_pos'):
                if (self.pre_pos != self.pos) and self.children[0].children:
                    self.parent.parent.sound.play('missed_placed')
                    Animation(
                        x=self.pre_pos[0], y=self.pre_pos[1],
                        t='linear', duration=.2).start(self)

    def get_colored_area(self, board, label, **kwargs):
        """
        To set found or untouched shape last position is available or
        not checked and placed shape is disappeared
        if all gone new set is called
        :param label:
        :param board:
        """
        plus_score = 0
        try:
            shape = kwargs.get('shape', self.children[0].children[0])
            shape_objs = shape.children
            shape_color = shape.color
            label_index = board.children.index(label)
            shape_box_on_board = shape_on_box(shape, label_index)
            occupied = check_occupied(board, shape_box_on_board, shape_objs)

            # Set color and remove shape
            if not occupied:
                index = plus_score = 0
                board_labels = []
                for i in shape_objs:
                    if str(i).find('Label') != -1:
                        board_label = board.children[shape_box_on_board[index]]
                        if str(board_label).find('Label') != -1:
                            board_label.filled = True
                        set_color(board_label, shape_color)
                        plus_score += 1
                        board_labels.append(shape_box_on_board[index])

                    index += 1

                parent = self.children[0]
                board.parent.sound.play('placed')
                parent.clear_widgets()
                root_class = parent.parent.parent.parent
                self.clear_lines(get_lines(board_labels),
                                 shape_labels=board_labels)
                if not filter(
                        lambda x: x,
                        map(lambda x: x.children[0].children,
                            parent.parent.parent.children)):
                    board.parent.sound.play('new_shapes')
                    root_class.coming_shapes()

            else:
                raise IndexError
        except IndexError:
            if self.pre_pos != self.pos:
                board.parent.sound.play('missed_placed')
            anim = Animation(
                x=self.pre_pos[0], y=self.pre_pos[1], t='linear', duration=.2)
            anim.start(self)

        active_shapes = map(lambda x: x[0], filter(lambda x: x,
                                                   map(lambda x: x.children[
                                                       0].children,
                                                       board.parent.coming.children)))

        possible_places = False
        free_place = []
        for shape in active_shapes:
            result, place = free_positions(board, shape)
            if result:
                free_place.extend(place)
            possible_places = possible_places or result

        board.parent.score += plus_score
        if not possible_places:
            board.parent.free_place = []
            CustomScatter.change_movement(board.parent)
        else:
            best_place = CustomScatter.find_best_place(board, free_place)
            board.parent.free_place = best_place

    def clear_lines(self, lines, score_update=True, shape_labels=None):
        """
        clear lines on rows and cols, first collect indexes then get points
        :param shape_labels:
        :param score_update:
        :param lines:
        """
        if shape_labels is None:
            shape_labels = []
        board = self.parent.parent.board
        all_labels = []
        all_colored_labels = []
        block_count = 0
        for line in lines:
            flag = True
            colored_labels = []
            labels = []
            for index in line:
                label = board.children[index]
                labels.append(label)
                colored_labels.append(get_color(label))
                if not hasattr(label, 'filled') or not label.filled:
                    flag = False
                    break
            if flag:
                block_count += 1
                all_labels.extend(labels)
                possible_split_area = set(labels).intersection(set(
                    map(lambda x: board.children[x], shape_labels)))
                split_position = 5
                if possible_split_area:
                    split_label = list(possible_split_area)[0]
                    split_position = labels.index(split_label)

                first = colored_labels[:split_position]
                rest = colored_labels[split_position:]
                first.reverse()
                all_colored_labels.extend([first, rest])
        if all_labels:
            self.parent.parent.sound.play('line_clear')
        for i in all_labels:
            i.filled = False
        for x in all_colored_labels:
            box = 1
            for y in x:
                anim = Animation(rgba=board.parent.labels,
                                 d=float(box) / 35, t='in_circ')
                anim.start(y)
                box += 1
        if score_update:
            plus_score = len(all_labels) + (
                (block_count > 0 and (
                    5 * (block_count - 1)
                ) or 0) * block_count)
            board.parent.score += plus_score

    @staticmethod
    def change_movement(board):
        """
        disables the movements of shapes.
        :param board:
        """
        scatters = [board.comingLeft, board.comingMid, board.comingRight]
        for scatter in scatters:
            scatter.do_translation_x = not scatter.do_translation_x
            scatter.do_translation_y = not scatter.do_translation_y
        board.set_record()
        if not board.popup:
            board.create_on_end_popup()

    @staticmethod
    def find_best_place(board, possible_places):
        """
        Find best place from the list.

        For now, only to reach to gain more points. More AI should be add.
        :param possible_places:
        :param board:
        """
        result = []
        for places in possible_places:
            clear_clearity = get_lines(places)
            points = len(places)
            cleared_lines = 0
            for line in clear_clearity:
                filled = map(
                    lambda x:
                    True if x in places else board.children[x].filled,
                    line)
                if not filter(lambda x: not x, filled):
                    cleared_lines += 1
                points += len(filter(lambda x: x, filled))
            points = points + (cleared_lines * 10) + ((cleared_lines - 1) * 5)
            result.append([places, points])
        return result and sorted(result,
                                 key=lambda x: x[1],
                                 reverse=True)[0][0] or []

    def locate(self, per_shape_width, per_shape_height, width, height, index):
        self.size_hint = (None, None)
        self.size = (max(width, self.min_size),
                     max(height, self.min_size))
        scatter_pos_x = (
                (per_shape_width * index) +
                (per_shape_width - self.size[0]) / 2)

        scatter_pos_y = ((per_shape_height - self.size[1]) / 2 -
                         (height < self.min_size and
                          (self.size[1] - height) / 2 or 0))
        self.pos = (scatter_pos_x, scatter_pos_y)
        self.pre_pos = self.pos
        if self.children[0].children:
            per_lbl = self.children[0].children[0].children[0].width
            shape = self.children[0].children[0]
            self.movement = (self.size[0] - per_lbl * shape.cols) / 2
            scatter_pos_x -= self.movement
            shape.pos = (self.movement, shape.pos[1])


class Sound(object):
    def __init__(self):
        try:
            for sound_name, sound_info in SOUNDS.items():
                sound_name = 'sound_' + sound_name
                sound = SoundLoader.load(sound_info['path'])
                sound.volume = sound_info['volume']
                sound.priority = sound_info['priority']
                setattr(self, sound_name, sound)
            self.sounds = self.get_sounds()
        except AttributeError:
            self.sounds = {}

    def get_sounds(self):
        keys = filter(lambda x: x.find('sound_') != -1, self.__dict__.keys())
        sounds = {}
        for key in keys:
            sounds.update({key: getattr(self, key)})
        return sounds

    def play(self, sound_key):
        """
        Play sound
        :param sound_key:
        """
        global SOUND
        sound_key = 'sound_' + sound_key
        if SOUND:
            try:
                played_sounds = filter(
                    lambda x: x[1].state == 'play', self.sounds.items())
                sound = getattr(self, sound_key)
                sound_on = False
                for sounds in played_sounds:
                    if (sounds[1].priority >= sound.priority or
                            sounds[1].priority == 0):
                        sounds[1].stop()
                    else:
                        sound_on = True
                if not sound_on:
                    sound.play()
            except AttributeError:
                pass

    def stop(self):
        try:
            sounds = map(lambda x: x, self.sounds.values())
            for sound in sounds:
                sound.stop()
        except AttributeError:
            pass


class Kivy1010(GridLayout):
    score = NumericProperty(0)
    visual_score = NumericProperty(0)
    high_score = NumericProperty(0)
    lightup_anim = []
    free_place = []
    free_place_notifier = ""
    theme = 'light'
    game_sound = None
    background = ''
    labels = ''
    popup = None
    info_popup = None
    last_move = None
    curve = 9
    font_size = 30

    def __init__(self):
        global SOUND
        super(Kivy1010, self).__init__()
        SOUND = DB.store_get('sound')
        self.set_theme()
        self.sound = Sound()
        self.high_score = get_record()
        self.popup = None
        self.go()
        # Clock.schedule_once(lambda x: self.check_update(), 5)
        Clock.schedule_once(lambda dt: self.update_score(), .04)
        self.movement_detect()

    def set_score(self):
        self.score = DB.store_get('score')

    def clear_free_place(self):
        for place in self.free_place:
            position = self.board.children[place]
            color = get_color(position)
            Animation.cancel_all(color, 'rgba')
            set_color(position, self.labels)

    def lightup(self):
        """to light up free space"""
        labels = []
        for index in self.free_place:
            labels.append(get_color(self.board.children[index]))
        for color in labels:
            anim = Animation(
                rgba=self.free_place_notifier, d=.5, t='linear')
            anim.start(color)

        theme = filter(lambda x: x != self.theme, THEME.keys())[0]
        if self.free_place_notifier == THEME[theme]['labels']:
            self.free_place_notifier = THEME[self.theme]['labels']
        else:
            self.free_place_notifier = THEME[theme]['labels']

    def update_score(self):
        if self.score > self.visual_score:
            self.visual_score += 1
        Clock.schedule_once(lambda dt: self.update_score(), .02)

    def movement_detect(self):
        """Calculate last movement on board."""
        if (self.free_place and
                (datetime.now() -
                 self.last_moved > timedelta(seconds=5))):
            self.lightup()
        Clock.schedule_once(lambda dt: self.movement_detect(), 1)

    def change_just_theme(self, *args):
        theme = filter(lambda x: x != self.theme, THEME.keys())[0]
        self.set_theme(theme=theme)
        self.keep_on()

    def change_theme(self, *args, **kwargs):
        theme = filter(lambda x: x != self.theme, THEME.keys())[0]
        self.set_theme(theme=theme)
        self.go()

    def set_theme(self, theme=None):
        if not theme:
            theme = DB.store_get('theme')
        self.theme = theme
        self.background = THEME.get(theme).get('background')
        self.labels = THEME.get(theme).get('labels')
        self.free_place_notifier = THEME[self.theme]['labels']
        self.change_board_color(self.labels)
        set_color(self.score_board.visual_score_label, self.background)
        set_color(self.score_board.high_score_label, self.background)
        Window.clearcolor = self.background
        pause_but = self.get_pause_but()
        if pause_but:
            set_color(pause_but, self.background)
        DB.store_put('theme', theme)
        DB.store_sync()

    def change_board_color(self, color):
        for label in self.board.children:
            if not label.filled:
                set_color(label, color)

    def get_pause_but(self, disability=True):
        try:
            button = filter(
                lambda x: str(x).find('Button') != -1,
                self.score_board.children)[0]
        except IndexError:
            button = None
        return button

    def pause_change_disability(self, attr=None):
        button = self.get_pause_but()
        try:
            button.disabled = attr if attr is not None else not self.disabled
            if button.disabled:
                button.image.source = 'assets/images/trans.png'
            else:
                button.image.source = 'assets/images/pause_%s.png' % (
                    self.theme == 'dark' and 'dark' or 'sun')
        except AttributeError:
            pass

    def create_pause_but(self):
        button = self.get_pause_but()
        if not button:
            button = Button(background_color=get_color_from_hex('E2DDD5'),
                            size_hint=(None, None), disabled=False)
            button.bind(on_press=self.create_on_start_popup)
        else:
            self.pause_change_disability(attr=False)
        button.bind(on_press=self.create_on_start_popup)
        button.image.source = 'assets/images/pause_%s.png' % (
            self.theme == 'dark' and 'dark' or 'sun')
        set_color(button, self.background)

    def remove_pause_but(self):
        button = self.get_pause_but()
        if button:
            self.pause_change_disability(attr=True)
            # self.score_board.remove_widget(button)
            # self.score_board.cols = 3

    def clear_lines(self, indexes):
        self.coming.children[0].clear_lines(indexes, score_update=False)

    def go(self, *args):
        try:
            try:
                button = args[0]
                if button.image.source == 'assets/images/refresh.png':
                    sync_score(0)
                    sync_board({})
            except IndexError:
                pass
            self.sound.play('game_on')
            self.create_pause_but()
            self.high_score = get_record()
            self.set_score()
            self.visual_score = 0
            if self.popup:
                self.popup.dismiss()
                self.popup = None
            self.refresh_board()
            self.coming_shapes()
            self.clear_lines(get_lines(range(0, 100)))
        except AttributeError:
            pass

    def keep_on(self, *args):
        try:
            self.create_pause_but()
            self.high_score = get_record()
            self.popup.dismiss()
            self.popup = None
        except AttributeError:
            pass

    def change_sound(self, *args):
        global SOUND
        button = args[0]
        SOUND = not SOUND
        button.image.source = 'assets/images/sound_%s.png' % (
            SOUND and 'on' or 'off')
        DB.store_put('sound', SOUND)
        DB.store_sync()
        if not SOUND:
            self.sound.stop()

    def check_update(self):
        release_link = "https://github.com/RedXBeard/kivy-1010/releases/latest"
        try:
            resp = urlopen(release_link)
            current_version = int("".join(resp.url.split("/")[-1].split(".")))
            lbl = Label(
                text="Already in Newest Version", shorten=True,
                strip=True, font_size=14, color=(0, 0, 0, 1))
            if current_version > int("".join(__version__.split('.'))):
                lbl.text = ("Newer Version Released please check\n"
                            "[color=3148F5][i][ref=https://github"
                            ".com/RedXBeard/kivy-1010]Kivy1010"
                            "[/ref][/i][/color]")
                lbl.bind(on_ref_press=open_page)

                layout = GridLayout(
                    cols=1, rows=1, spacing=(10, 10), padding=(3, 6, 3, 6))
                layout.add_widget(lbl)

                self.info_popup = Popup(
                    content=layout, size_hint=(None, None), size=(300, 200),
                    title='Kivy 1010', title_color=(0, 0, 0, 1),
                    border=(0, 0, 0, 0), auto_dismiss=True,
                    separator_color=get_color_from_hex('7B8ED4'))
                self.info_popup.open()
        except URLError:
            pass

    def generate_restart_button(self):
        """
        :return: Button
        """
        restart = Button(background_color=get_color_from_hex('EC9449'))
        restart.curve = 25
        set_color(restart, get_color_from_hex('EC9449'))
        restart.image.source = 'assets/images/refresh.png'
        restart.bind(on_press=self.go)
        return restart

    def generate_theme_button(self):
        """
        :return: Button
        """
        theme = Button(text_width=(self.width, None), halign='left')
        theme.curve = 25
        image_source = 'assets/images/moon.png'
        if self.theme == "dark":
            image_source = 'assets/images/sun.png'
        theme.image.source = image_source
        return theme

    def generate_sound_button(self):
        """
        :return: Button
        """
        sound = Button(background_color=get_color_from_hex('EC9449'))
        sound.curve = 25
        set_color(sound, get_color_from_hex('EC9449'))
        sound.image.source = 'assets/images/sound_%s.png' % (
            SOUND and 'on' or 'off'
        )
        sound.bind(on_press=self.change_sound)
        return sound

    def generate_score_label(self):
        """
        :param kwargs:
        :return: Label
        """
        score = self.score
        label = Label(
            text=str(score),
            color=get_color_from_hex('E2DDD5'))
        label.font_size = label.height / 3 * 2
        label.curve = 25
        set_color(label, get_color_from_hex('5BBEE5'))
        return label

    def create_on_start_popup(self, *args):
        if self.popup:
            self.popup.dismiss()
        self.remove_pause_but()

        gridlayout = GridLayout(
            cols=2, rows=1, spacing=(-20, 10), padding=(0, 0, 0, 0))

        button = generate_play_button()

        score_label = self.generate_score_label()
        medal_label = generate_medal_label()
        gridlayout.add_widget(medal_label)
        gridlayout.add_widget(score_label)

        layout = GridLayout(
            cols=1, rows=3, spacing=(10, 10), padding=(3, 6, 3, 6))

        if args and args[0].id != 'updater':
            restart = self.generate_restart_button()
            theme = self.generate_theme_button()
            button.bind(on_press=self.keep_on)
            theme.bind(on_press=self.change_just_theme)
            play_restart_box = GridLayout(cols=2, rows=1, spacing=(10, 0))
            play_restart_box.add_widget(button)
            play_restart_box.add_widget(restart)
            layout.add_widget(play_restart_box)

        else:
            theme = self.generate_theme_button()
            layout.add_widget(button)
            layout.add_widget(theme)
            button.bind(on_press=self.go)
            theme.bind(on_press=self.change_theme)

        layout.add_widget(gridlayout)
        sound_theme_box = GridLayout(cols=2, rows=1, spacing=(10, 0))
        sound = self.generate_sound_button()
        sound_theme_box.add_widget(theme)
        sound_theme_box.add_widget(sound)
        layout.add_widget(sound_theme_box)

        self.popup = Popup(
            content=layout, size_hint=(None, None),
            size=(Window.width / 3 * 2, Window.height / 3 * 2),
            title_color=(0, 0, 0, 1), auto_dismiss=False, border=(0, 0, 0, 0),
            separator_height=0)

        title = self.popup.children[0].children[2]
        self.popup.children[0].remove_widget(title)
        self.popup.open()

    def create_on_end_popup(self):
        self.remove_pause_but()
        label = Label(
            text='No Moves Left', color=get_color_from_hex('5BBEE5'),
            size_hint=(1, .3), font_size="25sp")
        label.curve = 25

        gridlayout = GridLayout(
            cols=1, rows=2, spacing=(0, 3))

        score_gridlayout = GridLayout(
            cols=2, rows=1, spacing=(-20, -10), padding=(0, 0, 0, 0))

        button = generate_play_button()
        button.bind(on_press=self.go)
        button.size_hint = (1, .5)

        score_label = self.generate_score_label()
        medal_label = generate_medal_label()
        score_gridlayout.add_widget(medal_label)
        score_gridlayout.add_widget(score_label)
        gridlayout.add_widget(label)
        gridlayout.add_widget(score_gridlayout)

        theme = self.generate_theme_button()
        theme.bind(on_press=self.change_theme)

        sound_theme_box = GridLayout(cols=2, rows=1, spacing=(10, 0),
                                     size_hint=(1, .5))
        sound = self.generate_sound_button()
        sound_theme_box.add_widget(theme)
        sound_theme_box.add_widget(sound)

        layout = GridLayout(
            cols=1, rows=3, spacing=(10, 10), padding=(3, 6, 3, 6))
        layout.add_widget(gridlayout)
        layout.add_widget(button)
        layout.add_widget(sound_theme_box)

        self.popup = Popup(
            content=layout, size_hint=(None, None),
            size=(Window.width / 3 * 2, Window.height / 3 * 2),
            auto_dismiss=False, border=(0, 0, 0, 0), separator_height=0)

        title = self.popup.children[0].children[2]
        self.popup.children[0].remove_widget(title)
        self.popup.open()
        sync_score(0)
        sync_board({})

    def set_record(self):
        try:
            high_score = DB.store_get('high_score')
        except KeyError:
            high_score = 0

        if high_score < self.score:
            DB.store_put('high_score', self.score)
        DB.store_sync()

    def refresh_board(self):
        self.board.clear_widgets()
        pre_board = get_synced_board()
        # wh = get_ratio()
        board_size = get_board_size()
        self.per_box = (board_size - 3 * 9) / 10
        for i in range(0, 100):
            label = Label(
                color=(0, 0, 0, 1), size_hint=(None, None),
                size=(self.per_box, self.per_box))
            label.curve = self.curve
            color = pre_board.get(str(99 - i), self.labels)
            set_color(label, color)
            if color != self.labels:
                label.filled = True
            self.board.add_widget(label)

    def get_shapes(self):
        result = []
        shape_sets = map(lambda x: x.children, self.coming.children)
        for s_set in shape_sets:
            if s_set and s_set[0].children:
                result.append(s_set[0].children[0])
        return result

    def coming_shapes(self):
        wh = get_ratio()
        shapes = get_synced_shapes()
        scatters = [self.comingLeft, self.comingMid, self.comingRight]
        for scatter in scatters:
            scatter.clear_widgets()
            scatter.pos = (0, 0)
            scatter.pre_pos = scatter.pos
        self.coming.height = self.get_shapes_size()
        per_shape_width = float(Window.width) / 3
        per_shape_height = float(self.coming.height)

        for scatter in scatters:
            scatter.calculate_shape_size(per_shape_width, per_shape_height)
            shape = None
            try:
                pre_shape = shapes[scatters.index(scatter)]
                shape = Shape(pre_shape['rows'], pre_shape['cols'],
                              pre_shape['array'], pre_shape['color'])
            except IndexError:
                pass
            if not shape:
                color_set = filter(
                    lambda x: x not in map(
                        lambda x: x.color, self.get_shapes()), COLOR)
                shape = Shape(color_set=color_set)
            width = 0
            height = 0
            index = 0
            for i in shape.array:
                if i == 1:
                    box = Label(
                        size_hint=(None, None),
                        size=(scatter.wh_per, scatter.wh_per))
                    box.curve = scatter.wh_per * wh / 3
                    set_color(box, self.background)
                else:
                    box = Image(
                        source='assets/images/trans.png',
                        size_hint=(None, None),
                        size=(scatter.wh_per, scatter.wh_per))
                index += 1
                if index % shape.cols == 0:
                    height += scatter.wh_per + 2

                if index % shape.rows == 0:
                    width += scatter.wh_per + 2
                shape.add_widget(box)
            shape.spacing = (2, 2)

            index = scatters.index(scatter)

            self.last_moved = datetime.now()
            scatter.add_widget(shape)
            scatter.locate(per_shape_width, per_shape_height,
                           width, height, index)
            label_colors = shape.get_colors()
            scatter.do_translation_y = True
            scatter.do_translation_x = True
            for color in label_colors:
                anim = Animation(rgba=shape.color, d=.2, t='in_circ')
                anim.start(color)

        DB.store_put('shapes', [])
        DB.store_sync()

    def get_shapes_size(self):
        score_board_height = get_scoreboard_height()
        return (float(Window.height) -
                float(self.board.height) -
                score_board_height)

    def resize_all(self, width, height):
        wh = get_ratio()
        try:
            score_board_height = get_scoreboard_height()
            (self.score_board.visual_score_label.width,
             self.score_board.visual_score_label.height) = (
                (width / 2) - (self.score_board.award_img.width / 2), score_board_height)
            self.score_board.width = width
            self.score_board.height = score_board_height + 30
            button = self.get_pause_but()
            button.image.size = (self.score_board.height / 4,
                                 self.score_board.height)
            button.width = self.score_board.height / 2
        except:
            pass

        try:
            board_size = get_board_size()
            padding = width > board_size and (width - board_size) / 2 or 40
            self.board.width = self.board.height = board_size
            self.per_box = (board_size - 3 * 9) / 10
            self.curve = wh * self.per_box / 3
            for label in self.board.children:
                label.width = label.height = self.per_box
                label.curve = self.curve
            top_padding = (height - (board_size / 2 * 3) - score_board_height) / 3
            self.board.padding = (padding, top_padding, padding, 0)
            self.padding = (0, 0, 0, 0)
        except:
            pass

        try:
            scatters = [self.comingLeft, self.comingMid, self.comingRight]
            self.coming.height = self.get_shapes_size()
            per_shape_width = float(width) / 3
            per_shape_height = float(self.coming.height)
            for scatter in scatters:
                scatter.calculate_shape_size(per_shape_width, per_shape_height)
                floatlayout = scatter.children[0]
                if floatlayout.children:
                    shape = floatlayout.children[0]
                    shape_width = 0
                    shape_height = 0
                    index = 0
                    for label in shape.children:
                        label.size = (scatter.wh_per, scatter.wh_per)
                        label.curve = scatter.wh_per * wh / 3
                        index += 1
                        if index % shape.cols == 0:
                            shape_height += scatter.wh_per + 2

                        if index % shape.rows == 0:
                            shape_width += scatter.wh_per + 2
                    index = scatters.index(scatter)
                    scatter.locate(per_shape_width, per_shape_height,
                                   shape_width, shape_height, index)
        except:
            pass


class KivyMinesApp(App):
    """Application main class"""

    def __init__(self, **kwargs):
        super(KivyMinesApp, self).__init__(**kwargs)
        Builder.load_file('assets/1010.kv')
        self.title = 'Kivy 1010'
        self.icon = 'assets/images/cube.png'

    def build(self):
        game = Kivy1010()
        Window.bind(on_resize=self.resize)
        Window.bind(on_close=self.save_board)
        Window.bind(on_stop=self.save_board)
        Window.bind(on_pause=self.save_board)
        game.resize_all(float(Window.width), float(Window.height))
        return game

    def on_pause(self):
        self.save_board()
        return True

    def on_stop(self):
        self.save_board()
        return True

    def restore(self, window):
        """Default window size handler.
        :param window:
        """
        window.size = WIN_SIZE

    def resize(self, *args):
        """Handle sizes of all widget on resizing of window."""
        window, width, height = args
        if False and (width < 520 or height < 600):
            self.restore(window)
        else:
            try:
                root = filter(
                    lambda x:
                    str(x).find('Kivy1010') != -1, window.children)[0]
                root.resize_all(float(root.width), float(root.height))
            except IndexError:
                pass

    def save_board(self, *args):
        """On exit keep last session"""
        try:
            window, = args
            root = window.children[0]
            board = root.board.children
            board_visual = {}
            if board:
                index = 0
                for label in board:
                    color = get_color(label)
                    if label.filled:
                        board_visual.update({index: color.rgba})
                    index += 1
            DB.store_put('board', board_visual)
            DB.store_put('score', root.score)
            DB.store_sync()
        except (ValueError, AttributeError):
            pass

        try:
            scatters = [root.comingLeft, root.comingMid, root.comingRight]
            shapes = []
            for scatter in scatters:
                layout = scatter.children[0]
                try:
                    shape = layout.children[0]
                    pre_shape = dict(rows=shape.rows,
                                     cols=shape.cols,
                                     array=shape.array,
                                     color=shape.color)
                    shapes.append(pre_shape)
                except IndexError:
                    pass
            DB.store_put('shapes', shapes)
            DB.store_sync()
        except (UnboundLocalError, AttributeError):
            pass


if __name__ == '__main__':
    Config.set('kivy', 'desktop', 1)
    # Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    KivyMinesApp().run()
