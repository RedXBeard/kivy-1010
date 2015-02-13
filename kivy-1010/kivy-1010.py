from kivy.app import App
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scatterlayout import Scatter
from kivy.uix.image import Image
from kivy.config import Config
from random import randint

SHAPES = [dict(cols=5, rows=1, array=[1, 1, 1, 1, 1]),
          dict(cols=4, rows=1, array=[1, 1, 1, 1]),
          dict(cols=3, rows=1, array=[1, 1, 1]),
          dict(cols=2, rows=1, array=[1, 1]),
          dict(cols=1, rows=5, array=[1, 1, 1, 1, 1]),
          dict(cols=1, rows=4, array=[1, 1, 1, 1]),
          dict(cols=1, rows=3, array=[1, 1, 1]),
          dict(cols=1, rows=2, array=[1, 1]),
          dict(cols=1, rows=1, array=[1]),

          dict(cols=2, rows=2, array=[1, 1, 1, 1]),
          dict(cols=3, rows=3, array=[1, 1, 1,
                                      1, 1, 1,
                                      1, 1, 1]),

          dict(cols=2, rows=2, array=[1, 1, 0, 1]),
          dict(cols=2, rows=2, array=[1, 0, 1, 1]),
          dict(cols=2, rows=2, array=[1, 1, 1, 0]),
          dict(cols=2, rows=2, array=[0, 1, 1, 1]),

          dict(cols=3, rows=3, array=[1, 1, 1,
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
                                      1, 1, 1])]

COLOR = [get_color_from_hex('990000'),
         get_color_from_hex('009900'),
         get_color_from_hex('000099')]


class Shape(GridLayout):
    def __init__(self):
        super(Shape, self).__init__()
        shape = SHAPES[randint(0, len(SHAPES) - 1)]
        color = COLOR[randint(0, len(COLOR) - 1)]
        self.rows = shape['rows']
        self.cols = shape['cols']
        self.array = shape['array']
        self.color = color


class CustomScatter(Scatter):
    def on_transform_with_touch(self, touch):
        super(CustomScatter, self).on_transform_with_touch(touch)

    def on_bring_to_front(self, touch):
        super(CustomScatter, self).on_bring_to_front(touch)

    def on_touch_up(self, touch):
        super(CustomScatter, self).on_touch_up(touch)

    def on_touch_down(self, touch):
        super(CustomScatter, self).on_touch_down(touch)


class Kivy1010(GridLayout):
    def __init__(self):
        super(Kivy1010, self).__init__()
        self.refresh_board()
        self.coming_shapes()

    def refresh_board(self):
        self.board.clear_widgets()
        for i in range(0, 100):
            label = Label(color=(0, 0, 0, 1), size_hint=(None, None), size=(30, 30))
            self.board.add_widget(label)

    def coming_shapes(self):

        scatters = [self.comingLeft, self.comingMid, self.comingRight]
        for scatter in scatters:
            scatter.clear_widgets()

        for scatter in scatters:
            shape = Shape()
            width = 0
            height = 0
            index = 0
            for i in shape.array:
                if i == 1:
                    box = Label(size_hint=(None, None), size=(30, 30))
                    color = filter(lambda x: str(x).find('Color') != -1, box.canvas.before.children)[0]
                    color.rgba = shape.color
                else:
                    box = Image(source='assets/trans.png', size_hint=(None, None), size=(30, 30))
                index += 1
                if index % shape.cols == 0:
                    height += 32

                if index % shape.rows == 0:
                    width += 32
                shape.add_widget(box)
            shape.spacing = (2, 2)
            scatter.add_widget(shape)
            scatter.size_hint = (None, None)
            scatter.size = (width, height)


class KivyMinesApp(App):
    def __init__(self, **kwargs):
        super(KivyMinesApp, self).__init__(**kwargs)
        Builder.load_file('assets/1010.kv')
        self.title = 'Kivy 1010'
        # self.icon = 'assets/mine.png'

    def build(self):
        mines = Kivy1010()
        return mines


if __name__ == '__main__':
    Window.clearcolor = (get_color_from_hex('F0F0F0'))
    Window.size = (520, 600)
    Config.set('kivy', 'desktop', 1)
    Config.set('graphics', 'fullscreen', 0)
    Config.set('graphics', 'resizable', 0)
    KivyMinesApp().run()