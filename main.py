__version__ = '1.5.0'

import webbrowser
from urllib2 import urlopen
from random import randint
from datetime import datetime, timedelta

from kivy.app import App
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.image import Image
from kivy.config import Config
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.core.audio import SoundLoader
from kivy.properties import NumericProperty
from config import DB, THEME, COLOR, SHAPES, SOUNDS, WIN_SIZE

# SCORE calculation
"""
1 - 0 - 0 - 0*5
2 - 10 - 5 - 1*5
3 - 30 - 10 - 2*5
4 - 60 - 15 - 3*5
5 - 100 - 20 - 4*5
"""

SOUND = False


def get_color(obj):
    u"""Color of widget returns."""
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
    """in row and in cols indexes are taken."""
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
    """
    pos_on_board = board.children
    place = False
    shape_box_on_board = []
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


class Shape(GridLayout):
    """
    Generate shapes from given already set list with random colour.
    """
    def __init__(
            self, rows=None, cols=None, array=None,
            color=None, color_set=COLOR):
        super(Shape, self).__init__()
        shape_key = SHAPES.keys()[randint(0, len(SHAPES.keys()) - 1)]
        shape = SHAPES[shape_key][randint(0, len(SHAPES[shape_key]) - 1)]
        ccolor = color_set[randint(0, len(color_set) - 1)]
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


class CustomScatter(ScatterLayout):
    """Shape class"""
    wh_per = 25
    last_moved = None

    def on_transform_with_touch(self, touch):
        """take action when shape touched."""
        super(CustomScatter, self).on_transform_with_touch(touch)
        root = self.parent.parent
        root.last_moved = datetime.now()
        root.clear_free_place()
        try:
            if self.do_translation_x and self.do_translation_y:
                shape = self.children[0].children[0]
                for label in shape.children:
                    label.size = (self.wh_per + 3, self.wh_per + 3)
                shape.spacing = (5, 5)
        except IndexError:
            pass

    def on_bring_to_front(self, touch):
        super(CustomScatter, self).on_bring_to_front(touch)

    def on_touch_up(self, touch):
        super(CustomScatter, self).on_touch_up(touch)
        self.reset_shape()
        self.position_calculation()

    def on_touch_down(self, touch):
        super(CustomScatter, self).on_touch_down(touch)

    def reset_shape(self):
        try:
            if self.do_translation_x and self.do_translation_y:
                shape = self.children[0].children[0]
                for label in shape.children:
                    label.size = (self.wh_per, self.wh_per)
                shape.spacing = (1, 1)
        except IndexError:
            pass

    def calculate_shape_size(self):
        wh = min((330 * Window.width / 520), (330 * Window.height / 600))
        self.wh_per = (wh / 11) - 5

    def position_calculation(self):
        """
        On board, taken scatter position is on a label or not check is handled
        """
        try:
            board = self.parent.parent.board
            labels = board.children
            obj_x, obj_y = self.pos
            flag = False
            for label in labels:
                pos_x, pos_y = label.pos
                lbl_wid, lbl_hei = label.size
                pos_x_check = pos_x - 6 <= obj_x <= pos_x + lbl_wid + 3
                pos_y_check = pos_y - 6 <= obj_y <= pos_y + lbl_hei + 3
                if pos_x_check and pos_y_check:
                    # position is available or not?
                    lbl_index = board.children.index(label)
                    line_left = (lbl_index / 10) * 10
                    shape = self.children[0].children[0]
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
                anim = Animation(
                    x=self.pre_pos[0], y=self.pre_pos[1],
                    t='linear', duration=.2)
                anim.start(self)

    def get_colored_area(self, board, label, **kwargs):
        """
        To set found or untouched shape last position is available or
        not checked and placed shape is disappeared
        if all gone new set is called
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
                self.clear_lines(get_lines(board_labels))
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
                            map(lambda x: x.children[0].children,
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

    def clear_lines(self, lines, score_update=True):
        """
        clear lines on rows and cols, first collect indexes then get points
        """
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
                all_colored_labels.extend(colored_labels)
        if all_labels:
            self.parent.parent.sound.play('line_clear')
        for i in all_labels:
            i.filled = False
        for i in all_colored_labels:
            anim = Animation(rgba=board.parent.labels, d=.9, t='in_out_back')
            anim.start(i)
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


class Sound(object):
    def __init__(self):
        for sound_name, sound_info in SOUNDS.items():
            sound_name = 'sound_' + sound_name
            setattr(self, sound_name, None)
            sound = getattr(self, sound_name)
            sound = SoundLoader.load(sound_info['path'])
            sound.volume = sound_info['volume']
            sound.priority = sound_info['priority']
            setattr(self, sound_name, sound)

    def get_sounds(self):
        keys = filter(lambda x: x.find('sound_') != -1, self.__dict__.keys())
        sounds = {}
        for key in keys:
            sounds.update({key: getattr(self, key)})
        return sounds

    def play(self, sound_key):
        """Play sound"""
        global SOUND
        sound_key = 'sound_' + sound_key
        if SOUND:
            played_sounds = filter(
                lambda x: x[1].state == 'play', self.get_sounds().items())
            sound = getattr(self, sound_key)
            for sounds in played_sounds:
                if sounds[1].priority >= sound.priority:
                    sounds[1].stop()
            sound.play()

    def stop(self):
        sounds = map(lambda x: x[1], self.get_sounds().items())
        for sound in sounds:
            sound.stop()


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

    def __init__(self):
        global SOUND
        super(Kivy1010, self).__init__()
        SOUND = DB.store_get('sound')
        self.set_theme()
        self.sound = Sound()
        self.high_score = self.get_record()
        self.popup = None
        self.create_on_start_popup()
        Clock.schedule_once(lambda x: self.check_update(), 5)
        Clock.schedule_once(lambda dt: self.update_score(), .03)
        # Not Yet complete. will be available on 1.5.0 version
        self.movement_detect()

    def set_score(self):
        self.score = DB.store_get('score')

    def sync_score(self, score):
        DB.store_put('score', score)
        DB.store_sync()

    def sync_board(self, board):
        DB.store_put('board', board)
        DB.store_sync()

    def get_synced_board(self):
        board = DB.store_get('board')
        return board

    def get_synced_shapes(self):
        shapes = DB.store_get('shapes')
        return shapes

    def clear_free_place(self):
        for place in self.free_place:
            position = self.board.children[place]
            color = get_color(position)
            Animation.cancel_all(color, 'rgba')
            set_color(position, self.labels)

    def lightup(self, *args):
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
        Clock.schedule_once(lambda dt: self.update_score(), .03)

    def movement_detect(self):
        """Calculate last movement on board."""
        if self.free_place and (
                datetime.now() - self.last_moved > timedelta(seconds=5)):
            self.lightup()
        Clock.schedule_once(lambda dt: self.movement_detect(), 1)

    def change_just_theme(self, *args):
        theme = filter(lambda x: x != self.theme, THEME.keys())[0]
        self.set_theme(theme=theme)
        self.keep_on()

    def change_theme(self, *args):
        theme = filter(lambda x: x != self.theme, THEME.keys())[0]
        self.set_theme(theme=theme)
        self.go()

    def set_theme(self, theme=None, *args):
        if not theme:
            theme = DB.store_get('theme')
        self.theme = theme
        self.background = THEME.get(theme).get('background')
        self.labels = THEME.get(theme).get('labels')
        self.free_place_notifier = THEME[self.theme]['labels']
        self.change_board_color(self.labels)
        Window.clearcolor = self.background
        DB.store_put('theme', theme)
        DB.store_sync()

    def change_board_color(self, color):
        for label in self.board.children:
            if not label.filled:
                set_color(label, color)

    def get_pause_but(self):
        try:
            button = filter(
                lambda x: str(x).find('Button') != -1,
                self.score_board.children)[0]
            button.disabled = not self.disabled
        except IndexError:
            button = None
        return button

    def create_pause_but(self):
        if not self.get_pause_but():
            button = Button(background_color=get_color_from_hex('E2DDD5'),
                            size_hint=(None, 1), width=50, disabled=False)
            button.bind(on_press=self.create_on_start_popup)
            button.image.source = 'assets/images/pause_%s.png' % (
                self.theme == 'dark' and 'dark' or 'sun')
            self.score_board.add_widget(button)

    def pause_change_disability(self):
        button = self.get_pause_but()
        try:
            button.disabled = not self.disabled
        except AttributeError:
            pass

    def remove_pause_but(self):
        button = self.get_pause_but()
        if button:
            self.score_board.remove_widget(button)

    def clear_lines(self, indexes):
        self.coming.children[0].clear_lines(indexes, score_update=False)

    def go(self, *args):
        try:
            try:
                button = args[0]
                if button.image.source == 'assets/images/refresh.png':
                    self.sync_score(0)
                    self.sync_board({})
            except IndexError:
                pass
            self.sound.play('game_on')
            self.create_pause_but()
            self.high_score = self.get_record()
            self.set_score()
            self.visual_score = 0
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
            self.high_score = self.get_record()
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

    def open_page(self, *args):
        webbrowser.open(args[1])

    def check_update(self, *args):
        release_link = "https://github.com/RedXBeard/kivy-1010/releases/latest"
        resp = urlopen(release_link)
        current_version = int("".join(resp.url.split("/")[-1].split(".")))
        lbl = Label(
            text="Already in Newest Version", shorten=True,
            strip=True, font_size=14, color=(0, 0, 0, 1))
        if current_version > int("".join(__version__.split('.'))):
            lbl.text = "Newer Version Released please check\n[color=3148F5][i]"
            lbl.text += "[ref=https://github.com/RedXBeard/kivy-1010]Kivy1010"
            lbl.text += "[/ref][/i][/color]"
            lbl.bind(on_ref_press=self.open_page)

            layout = GridLayout(
                cols=1, rows=1, spacing=(10, 10), padding=(3, 6, 3, 6))
            layout.add_widget(lbl)

            self.info_popup = Popup(
                content=layout, size_hint=(None, None), size=(300, 200),
                title='Kivy 1010', title_color=(0, 0, 0, 1),
                border=(0, 0, 0, 0), auto_dismiss=True,
                separator_color=get_color_from_hex('7B8ED4'))
            self.info_popup.open()

    def create_on_start_popup(self, *args):
        if self.popup:
            self.popup.dismiss()
        self.remove_pause_but()
        button = Button(background_color=get_color_from_hex('58CB85'))
        boxlayout = BoxLayout(orientation='vertical')
        set_color(boxlayout, get_color_from_hex('E2DDD5'))
        img = Image(source='assets/images/medal.png')
        label = Label(
            text=str(self.get_record()),
            color=get_color_from_hex('5BBEE5'),
            font_size=30)
        boxlayout.add_widget(img)
        boxlayout.add_widget(label)
        theme = Button(text_width=(self.width, None), halign='left')
        image_source = 'assets/images/moon.png'
        if self.theme == "dark":
            image_source = 'assets/images/sun.png'
        theme.image.source = image_source
        layout = GridLayout(
            cols=1, rows=3, spacing=(10, 10), padding=(3, 6, 3, 6))

        if args and args[0].id != 'updater':
            restart = Button(background_color=get_color_from_hex('EC9449'))
            restart.image.source = 'assets/images/refresh.png'
            restart.bind(on_press=self.go)
            button.bind(on_press=self.keep_on)
            theme.bind(on_press=self.change_just_theme)
            play_restart_box = GridLayout(cols=2, rows=1, spacing=(2, 0))
            play_restart_box.add_widget(button)
            play_restart_box.add_widget(restart)
            layout.add_widget(play_restart_box)

        else:
            layout.add_widget(button)
            button.bind(on_press=self.go)
            theme.bind(on_press=self.change_theme)

        layout.add_widget(boxlayout)
        sound_theme_box = GridLayout(cols=2, rows=1, spacing=(2, 0))
        sound = Button(background_color=get_color_from_hex('EC9449'))
        sound.image.source = 'assets/images/sound_%s.png' % (
            SOUND and 'on' or 'off'
        )
        sound.bind(on_press=self.change_sound)
        sound_theme_box.add_widget(theme)
        sound_theme_box.add_widget(sound)
        layout.add_widget(sound_theme_box)

        self.popup = Popup(
            content=layout, size_hint=(None, None), size=(200, 350),
            title='Kivy 1010', title_color=(0, 0, 0, 1), auto_dismiss=False,
            border=(0, 0, 0, 0), separator_color=get_color_from_hex('7B8ED4'))
        self.popup.open()

    def create_on_end_popup(self):
        global SOUND
        self.remove_pause_but()
        label1 = Label(
            text='No Moves Left', color=get_color_from_hex('5BBEE5'))
        img = Image(source='assets/images/medal.png')
        label2 = Label(
            text=str(self.score), font_size=30,
            color=get_color_from_hex('5BBEE5'))
        button = Button(background_color=get_color_from_hex('58CB85'))
        button.bind(on_press=self.go)

        boxlayout = BoxLayout(orientation='vertical')
        boxlayout.add_widget(label1)
        boxlayout.add_widget(img)
        boxlayout.add_widget(label2)

        theme = Button(text_width=(self.width, None), halign='left')
        theme.bind(on_press=self.change_theme)
        image_source = 'assets/images/moon.png'
        if self.theme == "dark":
            image_source = 'assets/images/sun.png'
        theme.image.source = image_source

        sound_theme_box = GridLayout(cols=2, rows=1, spacing=(2, 0))
        sound = Button(background_color=get_color_from_hex('EC9449'))
        sound.image.source = 'assets/images/sound_%s.png' % (
            SOUND and 'on' or 'off')
        sound.bind(on_press=self.change_sound)
        sound_theme_box.add_widget(theme)
        sound_theme_box.add_widget(sound)

        layout = GridLayout(
            cols=1, rows=3, spacing=(10, 10), padding=(3, 6, 3, 6))
        layout.add_widget(boxlayout)
        layout.add_widget(button)
        layout.add_widget(sound_theme_box)

        self.popup = Popup(
            content=layout, size_hint=(None, None), size=(200, 350),
            title='Kivy 1010', title_color=(0, 0, 0, 1), auto_dismiss=False,
            border=(0, 0, 0, 0), separator_color=get_color_from_hex('7B8ED4'))
        self.popup.open()
        self.sync_score(0)
        self.sync_board({})

    def set_record(self):
        try:
            high_score = DB.store_get('high_score')
        except KeyError:
            high_score = 0

        if high_score < self.score:
            DB.store_put('high_score', self.score)
        DB.store_sync()

    def get_record(self):
        try:
            high_score = DB.store_get('high_score')
        except KeyError:
            high_score = 0
        return high_score

    def refresh_board(self):
        self.board.clear_widgets()
        pre_board = self.get_synced_board()
        wh = min((330 * Window.width / 520), (330 * Window.height / 600))
        for i in range(0, 100):
            label = Label(
                color=(0, 0, 0, 1), size_hint=(None, None),
                size=(wh / 11, wh / 11))
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
        shapes = self.get_synced_shapes()
        scatters = [self.comingLeft, self.comingMid, self.comingRight]
        for scatter in scatters:
            scatter.clear_widgets()
            scatter.pos = (0, 0)
            scatter.pre_pos = scatter.pos

        per_shape_width = float(Window.width) / 3
        per_shape_height = float(self.coming.height)

        for scatter in scatters:
            scatter.calculate_shape_size()
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
                    set_color(box, self.background)
                else:
                    box = Image(
                        source='assets/images/trans.png',
                        size_hint=(None, None),
                        size=(scatter.wh_per, scatter.wh_per))
                index += 1
                if index % shape.cols == 0:
                    height += scatter.wh_per + 1

                if index % shape.rows == 0:
                    width += scatter.wh_per + 1
                shape.add_widget(box)
            shape.spacing = (1, 1)
            scatter.size_hint = (None, None)
            scatter.size = (width, height)

            index = scatters.index(scatter)
            scatter_pos_x = (
                per_shape_width * index) + (
                    (per_shape_width - scatter.size[0]) / 2)
            scatter_pos_y = (per_shape_height - scatter.size[1]) / 2
            scatter.pos = (scatter_pos_x, scatter_pos_y)
            scatter.pre_pos = scatter.pos
            self.last_moved = datetime.now()

            scatter.add_widget(shape)
            label_colors = shape.get_colors()
            scatter.do_translation_y = True
            scatter.do_translation_x = True
            for color in label_colors:
                anim = Animation(rgba=shape.color, d=.2, t='in_circ')
                anim.start(color)
        DB.store_put('shapes', [])
        DB.store_sync()

    def resize_all(self, width, height):
        try:
            self.score_board.visual_score_label.size = (
                width / 2 - 40, self.score_board.visual_score_label.size[1])
            self.score_board.width = width - 40
        except:
            pass

        try:
            wh = min((330.0 * width / 520), (330.0 * height / 600))
            padding = (width > wh) and (width - wh) / 2 - 20 or 0
            self.board.width = self.board.height = wh + 10
            for label in self.board.children:
                label.width = label.height = wh / 11
            self.board.padding = (padding, 10, padding, 10)
        except:
            pass

        try:
            scatters = [self.comingLeft, self.comingMid, self.comingRight]
            self.coming.height = (
                float(height) - float(self.board.height) - 50.0)
            per_shape_width = float(width) / 3
            per_shape_height = float(self.coming.height)
            for scatter in scatters:
                scatter.calculate_shape_size()
                floatlayout = scatter.children[0]
                if floatlayout.children:
                    shape = floatlayout.children[0]
                    shape_width = 0
                    shape_height = 0
                    index = 0
                    for label in shape.children:
                        label.size = (scatter.wh_per, scatter.wh_per)

                        if index % shape.cols == 0:
                            shape_height += scatter.wh_per + 1

                        if index % shape.rows == 0:
                            shape_width += scatter.wh_per + 1
                        index += 1
                    index = scatters.index(scatter)
                    scatter.size_hint = (None, None)
                    scatter.size = (shape_width, shape_height)
                    scatter_pos_x = (
                        (per_shape_width * index) + (
                            (per_shape_width - scatter.size[0]) / 2))
                    scatter_pos_y = max(
                        0, (per_shape_height - scatter.size[1]) / 2)
                    scatter.pos = (scatter_pos_x, scatter_pos_y)
                    scatter.pre_pos = scatter.pos
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
        mines = Kivy1010()
        Window.bind(on_resize=self.resize)
        Window.bind(on_close=self.save_board)
        return mines

    def restore(self, window):
        """Default window size handler."""
        window.size = WIN_SIZE

    def resize(self, *args):
        """Handle sizes of all widget on resizing of window."""
        window, width, height = args
        if width < 520 or height < 600:
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
        window, = args
        root = window.children[0]
        try:
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
        except AttributeError:
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
        except AttributeError:
            pass

if __name__ == '__main__':
    Window.size = WIN_SIZE
    Window.borderless = False
    Config.set('kivy', 'desktop', 1)
    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
    KivyMinesApp().run()
