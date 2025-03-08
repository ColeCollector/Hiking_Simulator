import pygame, random, sys, os

from scripts.platforms import Platforms
from scripts.feet import Feet
from scripts.menu import Menu
from scripts.GUI import GUI
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

        self.images = {}
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
        self.score = 0

        self.biome_stats = {'boulder' : {'color' : '#158BA5', 'transition' : 'transition_1', 'temp' :  0.00},
                            'snowy'   : {'color' : '#E4FFFF', 'transition' : 'transition_2', 'temp' : -0.05},
                            'bog'     : {'color' : '#ACC16A', 'transition' : 'transition_3', 'temp' :  0.00},
                            'beach'   : {'color' : '#FDE9BE', 'transition' : 'transition_4', 'temp' :  0.05},
                            'sewer'   : {'color' : '#404040', 'transition' : 'transition_5', 'temp' :  0.00}
                            }
        
        self.default_effects = {}

        self.overlay = pygame.Surface((WIDTH / 2, HEIGHT / 2), pygame.SRCALPHA)
        self.overlay.fill((0, 0, 0, 192))

        self.reset()
        self.game_status = 'menu'

    def reset(self):
        if self.highscore < self.score:
            self.highscore = round(self.score / 50)

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

        self.biomes = list(self.biome_stats.keys())
        self.biome = random.choice(self.biomes)
        self.biome = 'bog'

        self.biome_switch = random.randint(25, 40)
        self.last_biome_switch = 0
        self.last_biome = None
        self.bgcolor = "gray"

        self.snowflakes = []
        self.positions = []
        self.platforms = Platforms(self)

        self.effects = self.default_effects

        self.gui = GUI(self)

    def run(self):
        while True:
            # Get mouse position and self.scale it down
            self.pos = list(pygame.mouse.get_pos())
            self.pos[0] /= 2
            self.pos[1] /= 2

            self.mouse_buttons = pygame.mouse.get_pressed()
            
            if self.game_status == 'game' and self.mouse_buttons[0]:  # If left mouse button is pressed
                if is_within_circle(self.pos, (231 + 17, 5 + 17), 17):
                    self.game_status = 'settings'
                    first_run = True
                else:
                    self.feet.click()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                else:
                    self.feet.handle_event(event)

            if self.game_status == 'menu':
                Menu(self)
                self.reset()

            if self.game_status == 'settings':
                if first_run:
                    first_run = False
                    self.screen.blit(self.overlay, (0, 0))

                for x, label in enumerate(['Restart', 'Menu', 'Resume']):
                    pygame.draw.rect(self.screen, "#000000", (59, 176 + 35 * x, 151, 30))
                    show_text(self.screen, label, (134, 191 + 35 * x), 'white')

                if self.clicking:
                    if pygame.Rect(59, 176 + 35 + 35, 151, 30).collidepoint(self.pos) :
                        self.game_status = 'game'

                    elif pygame.Rect(59, 176 + 35, 151, 30).collidepoint(self.pos):
                        self.game_status = 'menu'

                    elif pygame.Rect(59, 176, 151, 30).collidepoint(self.pos):
                        self.game_status = 'game'
                        self.reset()

            elif self.game_status == 'game':
                # Changing the bg after the transition has past
                if self.bgcolor != self.biome_stats[self.biome]['color'] and (self.score / 50 > self.last_biome_switch + 14):
                    self.bgcolor = self.biome_stats[self.biome]['color']

                self.current_biome = self.last_biome if self.last_biome_switch + 10 > self.score / 50 else self.biome

                # Switching biomes
                if self.score / 50 > self.biome_switch:
                    self.last_biome = self.biome
                    
                    # Chooses a random biome (other than the currentbiome)
                    self.biomes = list(self.biome_stats.keys())
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

                for tree in self.platforms.trees:
                    self.screen.blit(tree[0], tree[1])
                
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

                if self.biome_stats[self.biome]['temp'] != 0:
                    self.temp += self.biome_stats[self.biome]['temp']

                else:
                    # Bringing temp level back to middle
                    if self.temp > 150: 
                        self.temp -= min(0.025, self.temp - 150)

                    elif self.temp < 150:
                        self.temp += 0.025

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

                elif self.current_biome == 'snowy':
                    # Generate Snowflakes
                    if self.snowflakes == []:
                        for _ in range(100):  # Number of snowflakes
                            x = random.randint(0, WIDTH + 500)
                            y = random.randint(-200, 0)
                            speed = random.randint(2, 4)
                            size = random.randint(2, 4)
                            angle = random.randint(2, 4)
                            self.snowflakes.append([x, y, speed, size, angle])
                
                self.gui.draw()
                
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