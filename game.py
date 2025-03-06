import pygame, random, sys, os

from scripts.platforms import Platforms
from scripts.feet import Feet
from scripts.menu import Menu
from scripts.utils import *

# self.screen Size
WIDTH, HEIGHT = 540, 960

class Game():
    def __init__(self):
        # Initialize Pygame
        pygame.init()

        self.display = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
        self.screen = pygame.Surface((WIDTH / 2, HEIGHT / 2))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Hiking Game")

        # Backround audio
        pygame.mixer.music.load('data/sounds/ambience.wav')
        pygame.mixer.music.set_volume(0.05)
        pygame.mixer.music.play(-1)

        self.sounds = [pygame.mixer.Sound('data/sounds/ow.wav'), pygame.mixer.Sound('data/sounds/jump.wav'), pygame.mixer.Sound('data/sounds/bone.mp3'), 
                       pygame.mixer.Sound('data/sounds/splash.mp3'), pygame.mixer.Sound('data/sounds/snow.mp3')]

        self.sounds[0].set_volume(0.1)
        self.sounds[1].set_volume(0.2)
        self.sounds[2].set_volume(0.5)
        self.sounds[3].set_volume(0.1)
        self.sounds[4].set_volume(0.1)

        files = os.listdir('data/images')
        self.images = {'foot_1' : pygame.transform.flip(pygame.image.load('data/images/shoes/foot.png'), True, False),
                       'foot_2' : pygame.image.load('data/images/shoes/foot.png')}
        
        self.shadows = {}

        for file in files:
            if '.png' in file:
                self.images[file.replace('.png', '')] = pygame.image.load(f'data/images/{file}')
            else:
                for item in os.listdir(f'data/images/{file}'):
                    self.images[item.replace('.png', '')] = pygame.image.load(f'data/images/{file}/{item}')

        for image in self.images.copy():
            self.images[f"{image}_flipped"] = pygame.transform.flip(self.images[image], True, False)

        self.walk_radius = [50, 50] 
        self.highscore = 0
        self.colors = {'bog':'#ACC16A', 'boulder':'#158BA5', 'snowy':'#E4FFFF', 'beach':'#FDE9BE', 'sewer' : '#404040'}

        self.reset()
        self.game_status = 'menu'

    def reset(self):
        self.feet = Feet(self)
        self.speed = 0 
        self.target = 0
        self.camera_y = 0
        self.velocity = 0
        self.score = 0
        self.scale = 0
        self.temp = 150
        self.stamina = 300
        self.clicking = False
        self.transition = -70
        self.dead = 0

        self.biomes = list(self.colors.keys())
        self.biome = random.choice(self.biomes)
        self.biome = 'bog'

        self.biome_switch = random.randint(25, 40)
        self.last_biome_switch = 0
        self.last_biome = None
        self.bgcolor = "gray"

        self.snowflakes = []
        self.positions = []
        self.platforms = Platforms(self)

        self.effects = {
            'slipchance' : 0, 
            'temp'       : 0, 
            'regen'      : 0.15, 
            'stamina'    : 0.08,
            'jump'       : 5
        }

    def run(self):
        while True:
            # Get mouse position and self.scale it down
            self.pos = list(pygame.mouse.get_pos())
            self.pos[0] /= 2
            self.pos[1] /= 2

            self.mouse_buttons = pygame.mouse.get_pressed()
            
            if self.game_status == 'game' and self.mouse_buttons[0]:  # If left mouse button is pressed
                self.feet.click()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                else:
                    self.feet.handle_event(event)

            if self.game_status == 'menu':
                Menu(self)

            elif self.game_status == 'game':
                # Changing the bg after the transition has past
                if self.bgcolor != self.colors[self.biome] and (self.score / 50 > self.last_biome_switch + 14):
                    self.bgcolor = self.colors[self.biome]

                self.current_biome = self.last_biome if self.last_biome_switch + 10 > self.score / 50 else self.biome

                # Switching biomes
                if self.score / 50 > self.biome_switch:
                    self.last_biome = self.biome
                    
                    # Chooses a random biome (other than the currentbiome)
                    self.biomes = list(self.colors.keys())
                    self.biomes.remove(self.biome)
                    self.biome = random.choice(self.biomes)
                    self.last_biome_switch = self.biome_switch
                    self.biome_switch += random.randint(25, 40)
                    self.platforms = Platforms(self)
                
                # Fill the self.screen with a color
                self.screen.fill(self.bgcolor)
                
                self.speed = max(round((self.target - self.speed) * 0.1), 0)
                self.target -= self.speed

                self.score += self.speed

                self.platforms.update()
                self.platforms.render()  
                self.platforms.collision_check()

                self.feet.draw(self.screen)

                if self.snowflakes != []:
                    # Update and draw snowflakes
                    for flake in self.snowflakes[::-1]:
                        flake[0] -= flake[2] * (flake[3] / 2)
                        flake[1] += flake[2]
                        if flake[1] > HEIGHT or flake[0] < 0:
                            if self.current_biome == 'snowy' :
                                flake[0] = random.randint(0, WIDTH)
                                flake[1] = random.randint(-20, -5)
                            else:
                                self.snowflakes.remove(flake)

                        pygame.draw.circle(self.screen, 'white', (flake[0], flake[1]), flake[3])

                for tree in self.platforms.trees:
                    self.screen.blit(tree[0],tree[1])
                
                if self.scale == 0:
                    self.feet.handle_collisions()

                else:
                    # Apply and slowly fade damage tint
                    damage_tint(self.screen, self.scale / (200 if self.current_biome == 'snowy' else 100))
                    self.scale -= 1

                # You take damage if temp is too low or high
                if self.temp + self.effects['temp'] <= 50:
                    self.stamina -= (50 - self.temp + self.effects['temp']) * self.effects['stamina']

                elif self.temp + self.effects['temp'] >= 250:
                    self.stamina -= (self.temp + self.effects['temp'] - 250) * self.effects['stamina']

                # Regeneration
                elif self.stamina < 300 and self.current_biome != 'snowy':
                    self.stamina += self.effects['regen']

                if self.current_biome == 'beach':
                    self.temp += 0.05

                elif self.current_biome == 'snowy':
                    self.temp -= 0.05
                    
                    # Generate Snowflakes
                    if self.snowflakes == []:
                        for _ in range(100):  # Number of snowflakes
                            x = random.randint(0, WIDTH + 500)
                            y = random.randint(-200, 0)
                            speed = random.randint(2, 4)
                            size = random.randint(2, 4)
                            angle = random.randint(2, 4)
                            self.snowflakes.append([x, y, speed, size, angle])
                
                # Bringing temp level back to middle
                elif self.temp > 150: 
                    self.temp -= min(0.025, self.temp - 150)

                elif self.temp < 150:
                    self.temp += 0.025

                # Mouse Position Circle
                pygame.draw.circle(self.screen, 'white', self.pos, 10, 1)
                pygame.draw.circle(self.screen, 'white', self.pos, 2)
                
                # Stamina bar
                pygame.draw.rect(self.screen, "#133672", (59, 44, 152, 12))
                pygame.draw.rect(self.screen, "#2B95FF", (60, 45, self.stamina / 2, 10))

                # Temperature bar
                pygame.draw.rect(self.screen, "#AFAFAF", (59, 64, 152, 12))
                pygame.draw.rect(self.screen, "#E00000", (60, 65, min(self.temp + self.effects['temp'], 300) / 2, 10))
                self.screen.blit(self.images['bar'], (36, 39))

                #-100 to 100 degrees celcius
                show_text(self.screen, f"{str(round((self.temp + self.effects['temp'] - 150) / 3))}°C", (113, 86), "white")

                # Displaying biome in bottom right (for testing)
                show_text(self.screen, str(self.current_biome), (245, 465), "black")
                
                self.screen.blit(self.images['highscore'], (2, 14))
                
                # Outlined Highscore text
                show_text(self.screen, str(self.highscore), (28, 23), 'black')
                show_text(self.screen, str(self.highscore), (30, 23), 'black')
                show_text(self.screen, str(self.highscore), (28, 21), 'black')
                show_text(self.screen, str(self.highscore), (30, 21), 'black')
                show_text(self.screen, str(self.highscore), (29, 22), 'white')

                # Displaying score
                show_text(self.screen, str(int(self.score / 50)), (137, 24), "black", 32)
                show_text(self.screen, str(int(self.score / 50)), (135, 22), "white", 32)

                # Visual effect when you get super hot
                heatwave_img = self.images['heatwave'].convert_alpha()
                heatwave_img.set_alpha(min(50, max(0, (self.temp + self.effects['temp'] - 200) * 0.5))) 
                self.screen.blit(heatwave_img, (0, 0))

                # You die if you run out of stamina
                if self.stamina <= 0 or self.transition == 70:   
                    self.transition = min(70, self.transition + 1)
                    self.dead += 1
                
                if self.transition < 0:
                    self.transition += 1

                if self.dead:
                    if self.dead >= 10:
                        self.transition = min(70, self.transition + 1)

                    if self.dead > 80:
                        # Resetting everything
                        if self.feet.wet_feet != 0: self.effects['temp'] += 30

                        if self.highscore < self.score:
                            self.highscore = round(self.score / 50)

                        self.reset()

                # The black circular transition
                transition_surf = pygame.Surface(self.screen.get_size())
                pygame.draw.circle(transition_surf, (255, 255, 255), (self.screen.get_width() // 2, self.screen.get_height() // 2), (70 - abs(self.transition)) * 8)
                transition_surf.set_colorkey((255, 255, 255))
                self.screen.blit(transition_surf, (0, 0))

            # Update the display
            self.display.blit(pygame.transform.scale(self.screen, self.display.get_size()), (0, 0))
            pygame.display.flip()
            self.clock.tick(60)
            self.clicking = False

Game().run()