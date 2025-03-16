import pygame, random

from scripts.utils import show_text


# self.screen Size
WIDTH, HEIGHT = 540, 960

class GUI:
    def __init__(self, game):
        self.game = game
        self.snowflakes = []
        self.raindrops = []
        self.rain_biome = ''

    def handle_weather(self):
        if self.snowflakes != []:
            # Update and draw snowflakes
            for flake in self.snowflakes[::-1]:
                flake[0] -= flake[2] * (flake[3] / 2)
                flake[1] += flake[2]
                if flake[1] > HEIGHT / 2 or flake[0] < 0:
                    if self.game.current_biome == 'snowy' :
                        flake[0] = random.randint(0, WIDTH + 200)
                        flake[1] = - 5
                    else:
                        self.snowflakes.remove(flake)

                pygame.draw.circle(self.game.screen, 'white', (flake[0], flake[1]), flake[3])

        elif self.game.current_biome == 'snowy':
            # Generate Snowflakes
            for _ in range(75):  # Number of snowflakes
                x = random.randint(0, WIDTH + 500)
                y = random.randint(-200, 0)
                speed = random.randint(2, 4)
                size = random.randint(2, 4)
                angle = random.randint(2, 4)
                self.snowflakes.append([x, y, speed, size, angle])

        if self.raindrops != []:
            # Update and draw snowflakes
            for drop in self.raindrops[::-1]:
                drop[0] -= 5
                drop[1] += 15
                if drop[1] > HEIGHT / 2 or drop[0] < 0:
                    if self.game.current_biome == self.rain_biome:
                        drop[0] = random.randint(0, WIDTH + 200)
                        drop[1] = - 5
                    else:
                        self.raindrops.remove(drop)

                pygame.draw.line(self.game.screen, 'light blue', (drop[0], drop[1]), (drop[0] - 10, drop[1] + 30), 2)

    def generate_rain(self, rain_biome):
        self.rain_biome = rain_biome
        for _ in range(100):  # Number of raindrops
            x = random.randint(0, WIDTH + 500)
            y = random.randint(-200, 0)
            self.raindrops.append([x, y])

    def draw(self):
        # Stamina bar
        pygame.draw.rect(self.game.screen, "#133672", (59, 44, 152, 12))
        pygame.draw.rect(self.game.screen, "#2B95FF", (60, 45, self.game.stamina / 2, 10))

        # Temperature bar
        pygame.draw.rect(self.game.screen, "#AFAFAF", (59, 64, 152, 12))
        pygame.draw.rect(self.game.screen, "#E00000", (60, 65, min(self.game.temp + self.game.effects['Temp'], 300) / 2, 10))
        self.game.screen.blit(self.game.images['bar'], (36, 39))

        #-100 to 100 degrees celcius
        show_text(self.game.screen, f"{str(round((self.game.temp + self.game.effects['Temp'] - 150) / 3))}°C", (113, 86), "white")

        # Displaying biome in bottom right (for testing)
        show_text(self.game.screen, str(self.game.current_biome), (245, 465), "black")
        
        self.game.screen.blit(self.game.images['highscore'], (2, 14))
        self.game.screen.blit(self.game.images['settings'], (231, 5))

        # Outlined Highscore text
        show_text(self.game.screen, str(self.game.highscore), (28, 23), 'black')
        show_text(self.game.screen, str(self.game.highscore), (30, 23), 'black')
        show_text(self.game.screen, str(self.game.highscore), (28, 21), 'black')
        show_text(self.game.screen, str(self.game.highscore), (30, 21), 'black')
        show_text(self.game.screen, str(self.game.highscore), (29, 22), 'white')

        # Displaying score
        show_text(self.game.screen, str(int(self.game.score / 50)), (137, 24), "black", 32)
        show_text(self.game.screen, str(int(self.game.score / 50)), (135, 22), "white", 32)

        # Mouse Position Circle
        pygame.draw.circle(self.game.screen, 'white', self.game.pos, 10, 1)
        pygame.draw.circle(self.game.screen, 'white', self.game.pos, 2)
        
        # Visual effect when you get super hot
        heatwave_img = self.game.images['heatwave'].convert_alpha()
        heatwave_img.set_alpha(min(50, max(0, (self.game.temp + self.game.effects['Temp'] - 200) * 0.5))) 
        self.game.screen.blit(heatwave_img, (0, 0))