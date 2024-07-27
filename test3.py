from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Line, Rectangle

class MyImage(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            self.line_color = Color(1, 1, 1, 1)  # White color
            self.line = Line(width=2, circle=(self.center_x, self.center_y, min(self.width, self.height) / 2))
        
        self.bind(pos=self.update_canvas, size=self.update_canvas)
    
    def update_canvas(self, *args):
        self.line.circle = (self.center_x, self.center_y, min(self.width, self.height) / 2)
        
class MyApp(App):
    def build(self):
        layout = BoxLayout()
        img = MyImage(source='your_image.png', size_hint=(None, None), size=(200, 200))
        layout.add_widget(img)
        return layout

if __name__ == '__main__':
    MyApp().run()
