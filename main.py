__version__ = '1.0.0'

from random import randint
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

from kivy.properties import NumericProperty

from config import DB, THEME, COLOR, SHAPES


def get_color(obj):
    try:
        obj_color = filter(lambda x: str(x).find('Color') != -1, obj.canvas.before.children)[0]
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
    shape_box_on_board = []
    line_left = (label_index / 10) * 10
    if shape.cols <= (label_index - line_left + 1):
        for i in range(0, shape.rows):
            row = range(label_index + i * 10, (label_index + i * 10) - shape.cols, -1)
            row.reverse()
            shape_box_on_board.extend(row)
    return shape_box_on_board


def check_occupied(board, board_row, shape_objs):
    occupied = False
    if not board_row:
        occupied = True
    index = 0
    for i in board_row:
        board_label = board.children[i]
        color = get_color(board_label)
        # CHECK
        if hasattr(board_label, 'filled') and board_label.filled:  # color.rgba != board.parent.labels:
            if str(shape_objs[index]).find('Label') != -1:
                occupied = True
        index += 1
    return occupied


def get_lines(indexes):
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
    pos_on_board = filter(lambda x: not x.filled,  # get_color(x).rgba == board.parent.labels,
                          board.children)
    place = None
    for pos in pos_on_board:
        label_index = board.children.index(pos)
        shape_objs = shape.children
        try:
            shape_box_on_board = shape_on_box(shape, label_index)
            occupied = check_occupied(board, shape_box_on_board, shape_objs)
            if occupied:
                raise IndexError
            place = True
            break
        except:
            pass
    return bool(place)


class Shape(GridLayout):
    def __init__(self):
        super(Shape, self).__init__()
        shape = SHAPES[randint(0, len(SHAPES) - 1)]
        color = COLOR[randint(0, len(COLOR) - 1)]
        self.rows = shape['rows']
        self.cols = shape['cols']
        self.array = shape['array']
        self.color = color

    def get_colors(self):
        result = []
        for ch in self.children:
            if str(ch).find('Label') != -1:
                result.append(get_color(ch))
        return result


class CustomAnimation(Animation):
    def __init__(self, wait_for=0, *args, **kwargs):
        super(CustomAnimation, self).__init__(*args, **kwargs)
        self.wait_for = wait_for

    def on_complete(self, widget):
        super(CustomAnimation, self).stop(widget)
        if str(widget).find('Color') == -1:
            if self.wait_for > 0:
                self.wait_for -= 1
            if self.wait_for == 0:
                scatters = widget.parent
                active_shapes = map(lambda x: x[0],
                                    filter(lambda x: x, map(lambda x: x.children[0].children, scatters.children)))
                possible_places = False
                for shape in active_shapes:
                    result = free_positions(scatters.parent.board, shape)
                    possible_places = possible_places or result
                if not possible_places:
                    CustomScatter.change_movement(scatters.parent)
                self.wait_for = -1


class CustomScatter(ScatterLayout):
    def on_transform_with_touch(self, touch):
        super(CustomScatter, self).on_transform_with_touch(touch)
        if self.do_translation_x and self.do_translation_y:
            shape = self.children[0].children[0]
            for label in shape.children:
                label.size = (30, 30)
            shape.spacing = (3, 3)

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
                    label.size = (25, 25)
                shape.spacing = (1, 1)
        except IndexError:
            pass

    def position_calculation(self):
        try:
            board = self.parent.parent.board
            labels = board.children
            obj_x, obj_y = self.pos
            flag = False
            for label in labels:
                pos_x, pos_y = label.pos
                lbl_wid, lbl_hei = label.size
                pos_x_check = pos_x - 3 <= obj_x <= pos_x + lbl_wid + 3
                pos_y_check = pos_y - 3 <= obj_y <= pos_y + lbl_hei + 3
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
            try:
                shape = self.children[0].children[0]
            except IndexError:
                shape = None
            anim = CustomAnimation(x=self.pre_pos[0], y=self.pre_pos[1], t='linear',
                                   duration=.2, wait_for=shape and shape.cols * shape.rows or 0)
            anim.start(self)

    def get_colored_area(self, board, label, **kwargs):
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
                parent.clear_widgets()
                root_class = parent.parent.parent.parent
                Clock.schedule_once(lambda dt: self.update_score(root_class, plus_score), .02)
                lines = get_lines(board_labels)
                self.clear_lines(lines)
                if not filter(lambda x: x, map(lambda x: x.children[0].children, parent.parent.parent.children)):
                    root_class.coming_shapes()
            else:
                raise IndexError
        except IndexError:
            try:
                shape = self.children[0].children[0]
            except IndexError:
                shape = None
            anim = CustomAnimation(x=self.pre_pos[0], y=self.pre_pos[1], t='linear',
                                   duration=.2, wait_for=shape and shape.cols * shape.rows or 0)
            anim.start(self)

    def update_score(self, scored_class, point):
        if point > 0:
            scored_class.score += 1
            Clock.schedule_once(lambda dt: self.update_score(scored_class, point - 1), .02)

    def clear_lines(self, lines):
        board = self.parent.parent.board
        all_labels = []
        all_colored_labels = []
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
                all_labels.extend(labels)
                all_colored_labels.extend(colored_labels)

        for i in all_labels:
            i.filled = False
        for i in all_colored_labels:
            anim = CustomAnimation(rgba=board.parent.labels, d=.9, t='in_out_back', wait_for=len(all_colored_labels))
            anim.start(i)
        Clock.schedule_once(lambda dt: self.update_score(board.parent, len(all_labels)), .02)

    @staticmethod
    def change_movement(board):
        scatters = [board.comingLeft, board.comingMid, board.comingRight]
        for scatter in scatters:
            scatter.do_translation_x = not scatter.do_translation_x
            scatter.do_translation_y = not scatter.do_translation_y
        board.set_record()
        if not board.popup:
            board.create_on_end_popup()


class Kivy1010(GridLayout):
    score = NumericProperty(0)
    high_score = NumericProperty(0)
    theme = 'light'
    background = ''
    labels = ''
    popup = None

    def __init__(self):
        super(Kivy1010, self).__init__()
        self.set_theme()
        self.high_score = self.get_record()
        self.popup = None
        self.create_on_start_popup()

    def change_theme(self, *args):
        theme = filter(lambda x: x != self.theme, THEME.keys())[0]
        self.set_theme(theme=theme)
        self.go()

    def change_theme_noreset(self, args):
        theme = filter(lambda x: x != self.theme, THEME.keys())[0]
        self.set_theme(theme=theme)
        self.keep_on()

    def set_theme(self, theme=None, *args):
        if not theme:
            theme = DB.store_get('theme')
        self.theme = theme
        self.background = THEME.get(theme).get('background')
        self.labels = THEME.get(theme).get('labels')
        Window.clearcolor = self.background
        DB.store_put('theme', theme)
        DB.store_sync()

    def get_pause_but(self):
        try:
            button = filter(lambda x: str(x).find('Button') != -1, self.score_board.children)[0]
            button.disabled = not self.disabled
        except IndexError:
            button = None
        return button

    def create_pause_but(self):
        if not self.get_pause_but():
            button = Button(background_color=get_color_from_hex('E2DDD5'), size_hint=(None, 1), width=50,
                            disabled=False)
            button.bind(on_press=self.create_on_start_popup)
            button.image.source = 'assets/pause_%s.png' % (self.theme == 'dark' and 'dark' or 'sun')
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

    def go(self, *args):
        self.create_pause_but()
        self.high_score = self.get_record()
        self.score = 0
        self.popup.dismiss()
        self.popup = None
        self.refresh_board()
        self.coming_shapes()

    def keep_on(self, *args):
        self.create_pause_but()
        self.high_score = self.get_record()
        self.popup.dismiss()
        self.popup = None

    def create_on_start_popup(self, *args):
        self.remove_pause_but()
        button = Button(background_color=get_color_from_hex('58CB85'))
        boxlayout = BoxLayout(orientation='vertical')
        set_color(boxlayout, get_color_from_hex('E2DDD5'))
        img = Image(source='assets/medal.png')
        label = Label(text=str(self.get_record()), color=get_color_from_hex('5BBEE5'), font_size=30)
        boxlayout.add_widget(img)
        boxlayout.add_widget(label)
        layout = GridLayout(cols=1, rows=3, spacing=(10, 10), padding=(3, 6, 3, 6))
        layout.add_widget(button)
        layout.add_widget(boxlayout)
        if args:
            button.bind(on_press=self.keep_on)
        else:
            button.bind(on_press=self.go)
            theme = Button(text_width=(self.width, None), halign='left')
            theme.image.source = self.theme == 'dark' and 'assets/sun.png' or 'assets/moon.png'
            theme.bind(on_press=self.change_theme)
            layout.add_widget(theme)

        self.popup = Popup(content=layout, size_hint=(None, None), size=(200, 300), title='Kivy 1010',
                           title_color=(0, 0, 0, 1), auto_dismiss=False, border=(0, 0, 0, 0),
                           separator_color=get_color_from_hex('7B8ED4'))
        self.popup.open()

    def create_on_end_popup(self):
        self.remove_pause_but()
        label1 = Label(text='No Moves Left', color=get_color_from_hex('5BBEE5'))
        img = Image(source='assets/medal.png')
        label2 = Label(text=str(self.score), font_size=30, color=get_color_from_hex('5BBEE5'))
        button = Button(background_color=get_color_from_hex('58CB85'))
        button.bind(on_press=self.go)
        boxlayout = BoxLayout(orientation='vertical')
        boxlayout.add_widget(label1)
        boxlayout.add_widget(img)
        boxlayout.add_widget(label2)
        theme = Button(text_width=(self.width, None), halign='left')
        theme.bind(on_press=self.change_theme)
        theme.image.source = self.theme == 'dark' and 'assets/sun.png' or 'assets/moon.png'
        layout = GridLayout(cols=1, rows=3, spacing=(10, 10), padding=(3, 6, 3, 6))
        layout.add_widget(boxlayout)
        layout.add_widget(button)
        layout.add_widget(theme)
        self.popup = Popup(content=layout, size_hint=(None, None), size=(200, 300), title='Kivy 1010',
                           title_color=(0, 0, 0, 1), auto_dismiss=False, border=(0, 0, 0, 0),
                           separator_color=get_color_from_hex('7B8ED4'))
        self.popup.open()

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
        for i in range(0, 100):
            label = Label(color=(0, 0, 0, 1), size_hint=(None, None), size=(30, 30))
            set_color(label, self.labels)
            self.board.add_widget(label)

    def coming_shapes(self):
        scatters = [self.comingLeft, self.comingMid, self.comingRight]
        for scatter in scatters:
            scatter.clear_widgets()
            scatter.pos = scatter.pre_pos
        for scatter in scatters:
            shape = Shape()
            width = 0
            height = 0
            index = 0
            for i in shape.array:
                if i == 1:
                    box = Label(size_hint=(None, None), size=(25, 25))
                    set_color(box, self.background)
                else:
                    box = Image(source='assets/trans.png', size_hint=(None, None), size=(25, 25))
                index += 1
                if index % shape.cols == 0:
                    height += 26

                if index % shape.rows == 0:
                    width += 26
                shape.add_widget(box)
            shape.spacing = (1, 1)
            scatter.size_hint = (None, None)
            scatter.size = (width, height)
            scatter.add_widget(shape)
            label_colors = shape.get_colors()
            scatter.do_translation_y = True
            scatter.do_translation_x = True
            for color in label_colors:
                anim = CustomAnimation(rgba=shape.color, d=.2, t='in_circ', wait_for=shape.cols * shape.rows)
                anim.start(color)


class KivyMinesApp(App):
    def __init__(self, **kwargs):
        super(KivyMinesApp, self).__init__(**kwargs)
        Builder.load_file('assets/1010.kv')
        self.title = 'Kivy 1010'
        self.icon = 'assets/cube.png'

    def build(self):
        mines = Kivy1010()
        return mines


if __name__ == '__main__':
    Window.size = (520, 600)
    Window.borderless = False
    Config.set('kivy', 'desktop', 1)
    Config.set('graphics', 'fullscreen', 0)
    Config.set('graphics', 'resizable', 0)
    KivyMinesApp().run()