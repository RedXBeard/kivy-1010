from kivy.app import App
from kivy.lang import Builder
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
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

          dict(cols=2, rows=2, array=[0, 0, 0, 0, 0,
                                      0, 0, 1, 1, 0,
                                      0, 0, 1, 1, 0,
                                      0, 0, 0, 0, 0,
                                      0, 0, 0, 0, 0]),
          dict(cols=3, rows=3, array=[0, 0, 0, 0, 0,
                                      0, 1, 1, 1, 0,
                                      0, 1, 1, 1, 0,
                                      0, 1, 1, 1, 0,
                                      0, 0, 0, 0, 0]),

          dict(cols=2, rows=2, array=[0, 0, 0, 0, 0,
                                      0, 0, 1, 1, 0,
                                      0, 0, 0, 1, 0,
                                      0, 0, 0, 0, 0,
                                      0, 0, 0, 0, 0]),
          dict(cols=2, rows=2, array=[0, 0, 0, 0, 0,
                                      0, 0, 1, 0, 0,
                                      0, 0, 1, 1, 0,
                                      0, 0, 0, 0, 0,
                                      0, 0, 0, 0, 0]),
          dict(cols=2, rows=2, array=[0, 0, 0, 0, 0,
                                      0, 0, 1, 1, 0,
                                      0, 0, 1, 0, 0,
                                      0, 0, 0, 0, 0,
                                      0, 0, 0, 0, 0]),
          dict(cols=2, rows=2, array=[0, 0, 0, 0, 0,
                                      0, 0, 0, 1, 0,
                                      0, 0, 1, 1, 0,
                                      0, 0, 0, 0, 0,
                                      0, 0, 0, 0, 0]),

          dict(cols=3, rows=3, array=[0, 0, 0, 0, 0,
                                      0, 1, 1, 1, 0,
                                      0, 1, 0, 0, 0,
                                      0, 1, 0, 0, 0,
                                      0, 0, 0, 0, 0]),
          dict(cols=3, rows=3, array=[0, 0, 0, 0, 0,
                                      0, 1, 1, 1, 0,
                                      0, 0, 0, 1, 0,
                                      0, 0, 0, 1, 0,
                                      0, 0, 0, 0, 0]),
          dict(cols=3, rows=3, array=[0, 0, 0, 0, 0,
                                      0, 1, 0, 0, 0,
                                      0, 1, 0, 0, 0,
                                      0, 1, 1, 1, 0,
                                      0, 0, 0, 0, 0]),
          dict(cols=3, rows=3, array=[0, 0, 0, 0, 0,
                                      0, 0, 0, 1, 0,
                                      0, 0, 0, 1, 0,
                                      0, 1, 1, 1, 0,
                                      0, 0, 0, 0, 0])]

COLOR = [get_color_from_hex('990000'),
         get_color_from_hex('009900'),
         get_color_from_hex('000099')]


class Shape(GridLayout):
    def __init__(self):
        super(Shape, self).__init__()
        shape = SHAPES[randint(0, len(SHAPES) - 1)]
        color = COLOR[randint(0, len(COLOR) - 1)]
        self.rows = 5  # shape['rows']
        self.cols = 5  # shape['cols']
        self.array = shape['array']
        self.color = color


class Kivy1010(GridLayout):
    def __init__(self):
        super(Kivy1010, self).__init__()
        self.refresh_board()
        self.coming_shapes()

    def refresh_board(self):
        self.board.clear_widgets()
        for i in range(0, 100):
            label = Label(text="%s" % i, color=(0, 0, 0, 1), size_hint=(None, None), size=(30, 30))
            self.board.add_widget(label)

    def coming_shapes(self):

        scatters = [self.comingLeft, self.comingMid, self.comingRight]
        for scatter in scatters:
            scatter.clear_widgets()

        for scatter in scatters:
            shape = Shape()
            for i in shape.array:
                label = Label(size_hint=(None, None), size=(20, 20))
                color = filter(lambda x: str(x).find('Color') != -1, label.canvas.before.children)[0]
                color.rgba = get_color_from_hex('F0F0F0')
                if i == 1:
                    color.rgba = shape.color
                shape.add_widget(label)

            shape.spacing = (1, 1)
            scatter.add_widget(shape)


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
    Window.size = (400, 600)
    Config.set('kivy', 'desktop', 1)
    Config.set('graphics', 'fullscreen', 0)
    Config.set('graphics', 'resizable', 0)
    KivyMinesApp().run()