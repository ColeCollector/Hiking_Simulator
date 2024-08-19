import random, math, pygame
from _utils import shadow

def image_variety(images, key):
    original = images[key]
    flipped = images[f"{key}_flipped"]

    return random.choice([original, flipped])
    
def rect_circle_intersect(rect, circle_center, circle_radius):
    #Check if any corner of the rectangle is inside the circle
    corners = [
        rect.topleft, 
        rect.topright, 
        rect.bottomleft, 
        rect.bottomright
    ]
    for corner in corners:
        if math.hypot(corner[0] - circle_center[0], corner[1] - circle_center[1]) <= circle_radius:
            return True

    #Check if any edge of the circle intersects with any edge of the rectangle
    closest_x = max(rect.left, min(circle_center[0], rect.right))
    closest_y = max(rect.top, min(circle_center[1], rect.bottom))
    distance_x = circle_center[0] - closest_x
    distance_y = circle_center[1] - closest_y
    return distance_x ** 2 + distance_y ** 2 <= circle_radius ** 2

def circles_intersect(circle1_pos, circle1_radius, circle2_pos, circle2_radius):
    # Calculate the distance between the centers of the circles
    distance = math.sqrt((circle1_pos[0] - circle2_pos[0])**2 + (circle1_pos[1] - circle2_pos[1])**2)

    # Check if the distance is less than the sum of the radii
    if distance < circle1_radius + circle2_radius:
        return True
    else:
        return False

class Platform:
    def __init__(self, biome, radius, pos, img, timer):
        self.biome = biome

        if radius == None:
            self.radius = radius

        elif type(radius) == list:self.radius = [radius[0]/2, radius[1]/2]
        else: self.radius = radius/2

        self.pos = [pos[0]/2, pos[1]/2]
        self.img = img
        self.timer = timer

    def update(self, speed, biome, platforms, banned):
        self.pos[1] += speed

        if self.pos[1] > 480:
            if self.biome == biome and self.img not in banned:
                self.pos[1] = -200
                self.pos[0] = 270 - self.pos[0] 
                self.timer = 0
            else: 
                platforms.remove(self)
        
    def render(self, screen, shadows, images, obstacles):
        if self.timer == 0:
            self.img.set_alpha(256)
            offset = 0

            if self.img in [images['log_1'], images["log_1_flipped"]]:
                offset = 16

            if self.radius != None:
                if self.img not in shadows:
                    if self.biome == 'boulder':
                        shadows[self.img] = [shadow(self.img, (21, 113, 208)), shadow(self.img, (206, 225, 245))]
                    else:
                        shadows[self.img] = shadow(self.img, (120, 165, 80))

                if self.biome == 'boulder':
                    screen.blit(shadows[self.img][0], (self.pos[0] - offset, self.pos[1]+6))
                    screen.blit(shadows[self.img][1], (self.pos[0] - offset, self.pos[1]+1))
                else:
                    screen.blit(shadows[self.img], (self.pos[0] - offset, self.pos[1]+3))
                
                if self.img == images['big_boulder']:
                    obstacles.append(self.pos)
                    
            screen.blit(self.img, (self.pos[0] - offset, self.pos[1]))
            
        else:
            self.img.set_alpha(self.timer)
            screen.blit(self.img, self.pos)
            self.timer -= 1


    def collision_check(self, collisions, feet, walkradius):
        if self.radius not in [None, 40] and self.timer == 0:
            if self.biome == 'boulder':
                collisions[0].append(circles_intersect(feet[0], walkradius[0]*0.85, [self.pos[0] + self.radius, self.pos[1] + self.radius], self.radius))
                collisions[1].append(circles_intersect(feet[1], walkradius[1]*0.85, [self.pos[0] + self.radius, self.pos[1] + self.radius], self.radius))

            elif self.biome == 'bog':
                collisions[0].append(rect_circle_intersect(pygame.Rect(self.pos+self.radius), feet[0], walkradius[0]*0.85))
                collisions[1].append(rect_circle_intersect(pygame.Rect(self.pos+self.radius), feet[1], walkradius[1]*0.85))

        else:
            collisions[0].append(False)
            collisions[1].append(False)

class Platforms:
    def __init__(self, platforms, images, new_biome):

        # This is so that we can add to the platforms
        if isinstance(platforms, Platforms): self.platforms = platforms.platforms
        else: self.platforms = platforms

        # Generating platforms based on the biome
        if new_biome == 'boulder':
            self.platforms.append(Platform('boulder', None, [0, -1400], images['transition_1'], 0))
            avoid = []

            for i in range(26):
                x = random.randint(0, 490)
                y = i*50 - 1800
                rand = random.randint(0, 1)

                self.platforms.append(Platform('boulder', [56, 45][rand], (x, y), [images['boulder'], images['boulder_2']][rand], 0))
                avoid.append([[x, y], [56, 45][rand]])

            self.platforms.append(Platform('boulder', 80, [100, 500 - 1350], images['big_boulder'], 0))
            avoid.append([[100, 500 - 1350], 80])
            
            for _ in range(10):
                x = random.randint(0, 520)
                y = random.randint(-350, 960) - 1400
                self.platforms.append(Platform('boulder', None, (x, y), image_variety(images, random.choice(['bubbles_1', 'bubbles_2', 'bubbles_3','bubbles_4'])), 0))

            for _ in range(10):

                while True:
                    x = random.randint(0, 520)
                    y = random.randint(-350, 960) - 1400

                    if not any(circles_intersect([item[0][0]+item[1],item[0][1]+item[1]], item[1], [x, y], 38) for item in avoid):
                        break
                avoid.append([[x, y], 38])

                self.platforms.append(Platform('boulder', None, (x, y), image_variety(images, random.choice(['green_lily', 'lily', 'flower_lily'])), 0))



        elif new_biome == 'bog':
            self.platforms.append(Platform('bog', None, (0, -1400), images['transition_3'], 0))

            for i in range(8):
                if random.randint(0, 1) == 0: x = random.randint(0, 100)
                else: x = random.randint(250, 500)
                y = i*120-1400
                self.platforms.append(Platform('bog', [100, 20], [x, y], image_variety(images, 'log_2'), 0))

            for i in range(2):
                x = random.randint(150, 200)
                y = i*600-1500
                self.platforms.append(Platform('bog', [90, 400], [x, y], image_variety(images, 'log_1'), 0))
            
            amount = [12, 6, 4, 18, 6]
            choices = ['shading', 'shading_2', 'shading_3', 'grass', 'rock']

            for i in range(5):
                for _ in range(amount[i]):
                    x = random.randint(0, 520)
                    y = random.randint(-400, 960) - 1400

                    selected_image = image_variety(images, choices[i])
                    self.platforms.append(Platform('bog', None, (x, y), selected_image, 0))
            
        elif new_biome == 'snowy':
            self.platforms.append(Platform('snowy', None, (0, -1400), images['transition_2'], 0))
            for _ in range(6):
                x = random.randint(0, 520)
                y = random.randint(-400, 960) - 1400

                self.platforms.append(Platform('snowy', None, (x, y), image_variety(images, 'stick'), 0))
        
        elif new_biome == 'beach':
            self.platforms.append(Platform('beach', None, (0, -1400), images['transition_4'], 0))
            for _ in range(25):
                x = random.randint(0, 520)
                y = random.randint(-400, 960) - 1400

                selected_image = image_variety(images, random.choices(['sand', 'sand_2', 'sand_3', 'sand_dollar', 'starfish', 'dead_grass'], weights=[26, 26, 26, 4, 8, 10])[0])
                self.platforms.append(Platform('beach', None, (x, y), selected_image, 0))

    def update(self, speed, biome, banned):
        for platform in self.platforms[::-1]:
            platform.update(speed, biome, self.platforms, banned)
    
    def render(self, screen, shadows, images):
        obstacles = []
        # Rendering the decorations first
        for platform in self.platforms:
            if platform.radius == None:
                platform.render(screen, shadows, images, obstacles)

        for platform in self.platforms:
            if platform.radius != None:
                platform.render(screen, shadows, images, obstacles)

        self.obstacles = obstacles

    def collision_check(self, feet, walkradius, clicked, slipchance):
        collisions = [[], []]

        for platform in self.platforms:
            platform.collision_check(collisions, feet, walkradius)
        
        if clicked:
            # Randomly falling platforms
            if random.randint(0, 6 - slipchance) == 0:
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

        self.platforms.append(Platform('snowy', None, pos, img, 0))