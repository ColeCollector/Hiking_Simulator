import random, pygame, os
from _utils import *

# Get a list of file names
files = os.listdir('images')
images = {}

for file in files:
    if '.png' in file:
        images[file.replace('.png', '')] = pygame.image.load(f'images/{file}')
    else:
        for item in os.listdir(f'images/{file}'):
            images[item.replace('.png', '')] = pygame.image.load(f'images/{file}/{item}')

for image in images.copy():
    images[f"{image}_flipped"] = pygame.transform.flip(images[image], True, False)

shadows = {}

def image_variety(images, key):
    original = images[key]
    flipped = images[f"{key}_flipped"]

    return random.choice([original, flipped])

class Platform:
    global images
    def __init__(self, biome, radius, pos, img, timer=0, reset=True):
        self.biome = biome
        self.radius = radius
        self.pos = list(pos)
        self.img = img
        self.timer = timer
        self.reset = reset

    def update(self, speed, biome, platforms):
        self.pos[1] += speed  

        if self.pos[1] > 480:
            if self.biome == biome and self.reset:
                self.pos[1] = -200 
                self.timer = 0
            else: 
                platforms.remove(self)

                # Spawning the sewer lid after all the ladders have spawned
                if self.biome == 'sewer' and self.reset and not images['sewer_lid'] in [p.img for p in platforms]:
                    platforms.append(Platform('sewer', None, (64, -180), images['sewer_lid'], reset=False))
        
    def render(self, screen, obstacles):
        if self.timer == 0:
            self.img.set_alpha(256)
            offset = 0

            if self.radius != None and self.biome == 'boulder':
                if self.img not in shadows:
                    shadows[self.img] = [shadow(self.img, (13, 109, 135)), shadow(self.img, (206, 225, 245))]

                screen.blit(shadows[self.img][0], (self.pos[0] - offset, self.pos[1] + 6))
                screen.blit(shadows[self.img][1], (self.pos[0] - offset, self.pos[1] + 1))

                if self.img == images['big_boulder']:
                    obstacles.append(self)

            screen.blit(self.img, (self.pos[0] - offset, self.pos[1]))
            
        else:
            self.img.set_alpha(self.timer)
            screen.blit(self.img, self.pos)
            self.timer -= 1

    def collision_check(self, collisions, feet, walkradius):
        if self.radius not in [None, 80] and self.timer == 0 :
            if self.biome == 'boulder':
                collisions[0].append(circles_intersect(feet[0], walkradius[0] * 0.85, [self.pos[0] + self.radius, self.pos[1] + self.radius], self.radius))
                collisions[1].append(circles_intersect(feet[1], walkradius[1] * 0.85, [self.pos[0] + self.radius, self.pos[1] + self.radius], self.radius))

            else:
                collisions[0].append(rect_circle_intersect(pygame.Rect(self.pos + self.radius), feet[0], walkradius[0] * 0.85))
                collisions[1].append(rect_circle_intersect(pygame.Rect(self.pos + self.radius), feet[1], walkradius[1] * 0.85))

        else:
            collisions[0].append(False)
            collisions[1].append(False)

class Platforms:
    global images
    def __init__(self, platforms, new_biome):
        
        # This is so that we can add to the platforms
        if isinstance(platforms, Platforms): self.platforms = platforms.platforms
        else: self.platforms = platforms
        
        transitions = {'boulder' : 'transition_1', 
                       'snowy'   : 'transition_2',
                       'bog'     : 'transition_3',
                       'beach'   : 'transition_4',
                       'sewer'  : 'transition_5'}
        
        self.platforms.append(Platform(new_biome, None, (0, -700), images[transitions[new_biome]], reset=False))

        # Generating platforms based on the biome
        if new_biome == 'boulder':
            self.platforms.append(Platform('boulder', 80, [50, -425], images['big_boulder']))
            avoid =[[50, -425, 70]]

            for i in range(26):
                x, y = random.randint(0, 245), i*25 - 900
                img = random.choice([images['boulder'], images['boulder_2']])
                size = img.get_height()
                counter = 1
                while counter < 15:   
                    counter += 1
                    if not any(circles_intersect([item[0] + item[2], item[1] + item[2]], item[2], [x + size, y + size], size) for item in avoid):
                        self.platforms.append(Platform('boulder', size, (x, y), img))
                        avoid.append([x, y, size])
                        break
                    
            self.biome_builder_2('boulder', 5, ['bubbles_1', 'bubbles_2', 'bubbles_3','bubbles_4'])

            amount = [25] * 2 + [19] * 3 + [13] * 8 + [8] * 10
            lilypads = {25 : 'lily_1', 19: 'lily_2', 13: 'lily_3', 8: 'lily_4'}

            for size in amount:
                x, y = random.randint(0, 260), random.randint(-900, -220)

                if not any(circles_intersect([item[0] + item[2], item[1] + item[2]], item[2], [x + size, y + size], size) for item in avoid):
                    avoid.append([x, y, size])
                    self.platforms.append(Platform('boulder', None, (x, y), image_variety(images, lilypads[size])))

        elif new_biome == 'bog':
            choices = [choice.replace('.png', '') for choice in os.listdir('images/bog_decor')]

            self.biome_builder_2('bog', 60, choices, [10, 6, 4, 3, 2, 2, 6, 6, 6, 6, 6, 6, 20, 20])
            self.biome_builder_1('bog', 2, [47, 200], 'log', [75, 100]) 
            self.biome_builder_1('bog', 8, [50, 10], 'ladder', [50, 100], True)     
            self.biome_builder_1('bog', 17, None, 'tree', [-43, 21], True)             

        elif new_biome == 'snowy':
            self.biome_builder_2('snowy', 6, ['stick'], [1])
        
        elif new_biome == 'beach':
            self.biome_builder_2('beach', 25, ['sand', 'sand_2', 'sand_3', 'sand_dollar', 'starfish'], [26, 26, 26, 4, 8])

        elif new_biome == 'sewer':
            for i in range(9):
                x, y = 110, (480 - (i * ((480 + 200) / 9)) - 710)
                if random.randint(0, 5) == 0: 
                    self.platforms.append(Platform('sewer', None, [x, y], image_variety(images, 'fallen_ladder'))) 
                else: 
                    self.platforms.append(Platform('sewer', [50, 10], [x, y], image_variety(images, 'sewer_ladder'))) 

    def biome_builder_1(self, biome, amount, size, img, threshold, flipped=False):
        for i in range(amount):
            image = image_variety(images, img)
            if flipped and random.randint(0, 1) == 0:
                x = random.randint(270 - threshold[1] - image.get_height(), 270 - threshold[0] - image.get_height())
            else: 
                x = random.randint(threshold[0], threshold[1])

            y = (480 - (i * ((480 + 200) / amount)) - 700 - image.get_height())
            self.platforms.append(Platform(biome, size, [x, y], image)) 

    def biome_builder_2(self, biome, amount, choices=[], weights=None):
        for _ in range(amount):
            x, y = random.randint(0, 260), random.randint(-900, -220)

            selected_image = image_variety(images, random.choices(choices, weights=weights)[0])
            self.platforms.append(Platform(biome, None, (x, y), selected_image))

    def update(self, speed, biome):
        for platform in self.platforms[::-1]:
            platform.update(speed, biome, self.platforms)
    
    def render(self, screen):
        obstacles = []
        trees = []

        # Rendering the decorations first
        for platform in self.platforms:
            if platform.img in [images['tree'], images["tree_flipped"]]:
                trees.append([platform.img, platform.pos])

            elif platform.radius == None:
                platform.render(screen, obstacles)

        for platform in self.platforms:
            if platform.radius != None and platform.img not in [images['tree'], images["tree_flipped"]]:
                platform.render(screen, obstacles)

        self.trees = trees
        self.obstacles = obstacles

    def collision_check(self, feet, walkradius, clicked, slipchance):
        collisions = [[], []]

        for platform in self.platforms:
            platform.collision_check(collisions, feet, walkradius)
        
        if clicked:
            # Randomly falling platforms
            if random.randint(0, 8 - slipchance) == 0:
                ontop = [i for sublist in collisions for i, value in enumerate(sublist) if value]
                
                # If we are ontop of a platform
                if len(ontop) != 0:
                    randplatform = random.choice(ontop)
                    if self.platforms[randplatform].biome == 'boulder' and self.platforms[randplatform].timer == 0:
                        self.platforms[randplatform].timer = 180
                        
        self.collisions = collisions

    def footprint(self, platforms, pos, img):
        # This is so that we can add to the platforms
        if isinstance(platforms, Platforms): self.platforms = platforms.platforms
        else: self.platforms = platforms

        self.platforms.append(Platform('snowy', None, pos, img, reset=False))