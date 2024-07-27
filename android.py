from kivy.app import App
from kivy.uix.image import Image
from kivy.uix.floatlayout import FloatLayout
from kivy.animation import Animation
from kivy.config import Config
from kivy.core.window import Window
from kivy.graphics import Color, Line

# Set the size of the window
Config.set('graphics', 'width', '450')
Config.set('graphics', 'height', '900')

class RingedImage(Image):
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
        layout = FloatLayout()

        # Load and display the images
        self.images = []

        for i in range(2):
            img = RingedImage(source='images/foot.png', size_hint=(None, None))
            img.size = img.texture_size
            img.pos = (Window.width / 2 - img.width / 2 + (i * 200), Window.height / 2 - img.height / 2)  # Position them side by side
            self.images.append(img)
            layout.add_widget(img)

        # Bind keyboard input events
        Window.bind(on_key_down=self.on_key_down)

        return layout

    def on_key_down(self, window, keycode, *args):
        # KEYCODES:
        # 97  : "A"
        # 100 : "D"

        keycodes = {97: 'a', 100: 'd'}
        
        if keycode in keycodes:
            if keycodes[keycode] == 'a': 
                self.animate_image(self.images[0], self.images[0].y + 50)
                self.animate_image(self.images[1], self.images[1].y - 50)

            elif keycodes[keycode] == 'd':
                self.animate_image(self.images[0], self.images[0].y - 50)
                self.animate_image(self.images[1], self.images[1].y + 50)

    def animate_image(self, image, new_y):
        # Create an animation to move the image to the new y position
        anim = Animation(y=new_y, duration=0.1)  # Adjust 'duration' as needed
        anim.start(image)

if __name__ == '__main__':
    MyApp().run()
