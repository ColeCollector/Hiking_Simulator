import random, pygame, os

from scripts.utils import *

def image_variety(images, key):
    original = images[key]
    flipped = images[f"{key}_flipped"]

    return random.choice([original, flipped])

class Platform:
    def __init__(self, game, biome, radius, pos, img, opacity=255, reset=True):
        self.game = game
        self.shadows = self.game.shadows
        self.biome = biome
        self.radius = radius
        self.pos = list(pos)
        self.img = img
        self.opacity = opacity
        self.reset = reset

    def update(self):
        self.pos[1] += self.game.speed

        if self.opacity == 0:
            self.game.positions.remove(self)

        elif self.pos[1] > 480:
            if self.biome == self.game.biome and self.reset:
                self.pos[1] = -200 
            else: 
                self.game.positions.remove(self)

                # Spawning the sewer lid after all the ladders have spawned
                if self.biome == 'sewer' and self.reset and not self.game.images['sewer_lid'] in [p.img for p in self.game.positions]:
                    self.game.positions.append(Platform(self.game, 'sewer', None, (64, -180), self.game.images['sewer_lid'], reset=False))
        
    def render(self):
        # The log needs to be offset since it's image is bigger than it's hitbox
        offset = 8 if self.img in [self.game.images['log'], self.game.images["log_flipped"]] else 0

        if self.opacity == 255:
            self.img.set_alpha(255)
            if self.radius != None and self.biome == 'boulder':
                if self.img not in self.shadows:
                    self.shadows[self.img] = [shadow(self.img, (13, 109, 135)), shadow(self.img, (206, 225, 245))]

                self.game.screen.blit(self.shadows[self.img][0], (self.pos[0] - offset, self.pos[1] + 6))
                self.game.screen.blit(self.shadows[self.img][1], (self.pos[0] - offset, self.pos[1] + 1))

                if self.img == self.game.images['big_boulder']:
                    self.game.platforms.obstacles.append(self)
        else:
            self.img.set_alpha(self.opacity)
            self.opacity -= 2
            
        self.game.screen.blit(self.img, (self.pos[0] - offset, self.pos[1]))
        
    def collision_check(self):
        if self.radius not in [None, 80] and self.opacity == 255:
            if self.biome == 'boulder':
                self.game.platforms.collisions[0].append(rect_circle_intersect(self.game.feet.hitbox[0], [self.pos[0] + self.radius, self.pos[1] + self.radius], self.radius))
                self.game.platforms.collisions[1].append(rect_circle_intersect(self.game.feet.hitbox[1], [self.pos[0] + self.radius, self.pos[1] + self.radius], self.radius))

            else:
                self.game.platforms.collisions[0].append(self.game.feet.hitbox[0].colliderect(pygame.Rect(self.pos + self.radius)))
                self.game.platforms.collisions[1].append(self.game.feet.hitbox[1].colliderect(pygame.Rect(self.pos + self.radius)))

        else:
            self.game.platforms.collisions[0].append(False)
            self.game.platforms.collisions[1].append(False)

class Platforms:
    def __init__(self, game):
        self.game = game

        self.obstacles = []
        self.collisions = []
        
        transitions = {'boulder' : 'transition_1', 
                       'snowy'   : 'transition_2',
                       'bog'     : 'transition_3',
                       'beach'   : 'transition_4',
                       'sewer'  : 'transition_5'}
        
        self.game.positions.append(Platform(self.game, self.game.biome, None, (0, -700), self.game.images[transitions[self.game.biome]], reset=False))

        # Generating platforms based on the biome
        if self.game.biome == 'boulder':
            self.game.positions.append(Platform(self.game, 'boulder', 80, [50, -425], self.game.images['big_boulder']))
            avoid =[[50, -425, 80]]

            for i in range(26):
                x, y = random.randint(0, 245), i * 25 - 900
                img = random.choice([self.game.images['boulder'], self.game.images['boulder_2']])
                size = img.get_height() / 2

                counter = 0
                while counter < 10:
                    counter += 1
                    if not any(circles_intersect([item[0] + item[2], item[1] + item[2]], item[2], [x + size, y + size], size) for item in avoid):
                        self.game.positions.append(Platform(self.game, 'boulder', size, (x, y), img))
                        avoid.append([x, y, size])
                        break
                    
            amount = [25] * 10 + [19] * 15 + [13] * 20 + [8] * 25
            lilypads = {25 : 'lily_1', 19: 'lily_2', 13: 'lily_3', 8: 'lily_4'}

            for size in amount:
                x, y = random.randint(0, 260), random.randint(-900, -220)

                if not any(circles_intersect([item[0] + item[2], item[1] + item[2]], item[2], [x + size, y + size], size) for item in avoid):
                    avoid.append([x, y, size])
                    self.game.positions.append(Platform(self.game, 'boulder', None, (x, y), image_variety(self.game.images, lilypads[size])))

        elif self.game.biome == 'bog':
            choices = [choice.replace('.png', '') for choice in os.listdir('data/images/bog_decor')]

            self.biome_builder_2('bog', 60, choices, [10, 6, 4, 3, 2, 2, 6, 6, 6, 6, 6, 6, 20, 20])
            self.biome_builder_1('bog', 2, [47, 200], 'log', [75, 100]) 
            self.biome_builder_1('bog', 8, [50, 10], 'ladder', [50, 100], True)     

            for i in range(20):
                image = image_variety(self.game.images, 'tree')
                if i % 2 == 0:
                    x = random.randint(270 - 43 - image.get_height(), 270 + 60 - image.get_height())
                else: 
                    x = random.randint(-60, 43)

                y = (480 - (i * ((480 + 200) / 22)) - 700 - image.get_height())
                self.game.positions.append(Platform(self.game, 'bog', None, [x, y], image)) 

        elif self.game.biome == 'snowy':
            self.biome_builder_2('snowy', 6, ['stick'], [1])
        
        elif self.game.biome == 'beach':
            self.biome_builder_2('beach', 25, ['sand', 'sand_2', 'sand_3', 'sand_dollar', 'starfish'], [26, 26, 26, 4, 8])

        elif self.game.biome == 'sewer':
            for i in range(9):
                x, y = 110, (480 - (i * ((480 + 200) / 9)) - 710)
                if random.randint(0, 5) == 0: 
                    self.game.positions.append(Platform(self.game, 'sewer', None, [x, y], image_variety(self.game.images, 'fallen_ladder'))) 
                else: 
                    self.game.positions.append(Platform(self.game, 'sewer', [50, 10], [x, y], image_variety(self.game.images, 'sewer_ladder'))) 

    def biome_builder_1(self, biome, amount, size, img, threshold, flipped=False):
        for i in range(amount):
            image = image_variety(self.game.images, img)
            if flipped and random.randint(0, 1) == 0:
                x = random.randint(270 - threshold[1] - image.get_height(), 270 - threshold[0] - image.get_height())
            else: 
                x = random.randint(threshold[0], threshold[1])

            y = (480 - (i * ((480 + 200) / amount)) - 700 - image.get_height())
            self.game.positions.append(Platform(self.game, biome, size, [x, y], image)) 

    def biome_builder_2(self, biome, amount, choices=[], weights=None):
        for _ in range(amount):
            x, y = random.randint(0, 260), random.randint(-900, -220)

            selected_image = image_variety(self.game.images, random.choices(choices, weights=weights)[0])
            self.game.positions.append(Platform(self.game, biome, None, (x, y), selected_image))

    def update(self):
        for pos in self.game.positions[::-1]:
            pos.update()
    
    def render(self):
        self.obstacles = []
        self.trees = []

        # Rendering the decorations first
        for pos in self.game.positions:
            if pos.img in [self.game.images['tree'], self.game.images["tree_flipped"]]:
                self.trees.append([pos.img, pos.pos])

            elif pos.radius == None:
                pos.render()

        for pos in self.game.positions:
            if pos.radius != None and pos.img not in [self.game.images['tree'], self.game.images["tree_flipped"]]:
                pos.render()

    def collision_check(self):
        self.collisions = [[], []]

        for platform in self.game.positions:
            platform.collision_check()
        
        if self.game.clicking:
            # Randomly falling platforms
            if random.randint(0, 12 - self.game.effects['slipchance']) == 0:
                on_top = [i for sublist in self.collisions for i, value in enumerate(sublist) if value and self.game.positions[i].biome == "boulder"]

                # If we are on_top of a platform
                if len(on_top) != 0:
                    random_platform = random.choice(on_top)
                    self.game.positions[random_platform].opacity = 128