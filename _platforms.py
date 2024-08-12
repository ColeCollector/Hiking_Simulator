import random, math, pygame

#THIS IS A PART OF _CLEAN.PY - AN ATTEMPT TO CLEAN UP THE CODE IN HIKING.PY   

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

log1 = pygame.image.load('images/log_1.png')

class Platform:
    def __init__(self, biome, radius, pos, img, timer):
        self.biome = biome

        if radius == None:
            self.radius = radius

        elif type(radius) == list:
            self.radius = [radius[0]/2,radius[1]/2]

        else:
            self.radius = radius/2

        self.pos = [pos[0]/2,pos[1]/2]
        self.img = img
        self.timer = timer

    def update(self, speed, biome, platforms, banned):
        self.pos[1] += speed

        if self.pos[1] > 960:
            if self.biome == biome and self.img not in banned:
                self.pos[1] = - 400/2
                self.timer = 0
            else: 
                platforms.remove(self)
        
    def render(self, screen, shadows, images):
        if self.timer == 0:
            #if self.biome == 'boulder':
            self.img.set_alpha(256)

            if self.img == images['log1']:
                
                screen.blit(shadows[self.img], (self.pos[0]-16, self.pos[1]+3))
                screen.blit(self.img, (self.pos[0]-16, self.pos[1]))
                #pygame.draw.rect(screen, "red", (self.pos+self.radius))

            else:
                if self.radius != None:
                    screen.blit(shadows[self.img], (self.pos[0], self.pos[1]+3))
                screen.blit(self.img, self.pos)
            
        else:
            self.img.set_alpha(self.timer)
            screen.blit(self.img, self.pos)
            self.timer -= 1

    def collision_check(self, collisions, feet, walkradius):
        if self.radius != None:
            if self.biome == 'boulder':
                collisions[0].append(circles_intersect(feet[0], walkradius[0]*0.8, [self.pos[0], self.pos[1]], self.radius))
                collisions[1].append(circles_intersect(feet[1], walkradius[1]*0.8, [self.pos[0], self.pos[1]], self.radius))

            elif self.biome == 'bog':
                collisions[0].append(rect_circle_intersect(pygame.Rect(self.pos+self.radius), feet[0], walkradius[0]*0.8))
                collisions[1].append(rect_circle_intersect(pygame.Rect(self.pos+self.radius), feet[1], walkradius[1]*0.8))

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
            self.platforms.append(Platform('boulder', None, [0, -1400], images['transition4'], 0))

            for i in range(26):
                x = random.randint(0, 490)
                y = i*50 - 1800
                randomchoice = random.randint(0, 2)
                self.platforms.append(Platform('boulder', ([56, 56, 45][randomchoice]), (x, y), [images['boulder'], 
                images['fboulder'], images['boulder2']][randomchoice], 0))

            for _ in range(25):
                x = random.randint(0, 520)
                y = random.randint(-400, 960) - 1350
                self.platforms.append(Platform('boulder', None, (x, y), 
                random.choices([images['sand'], images['sand_2'], images['sand_3'], images['sand_dollar'], images['starfish']], weights=[29, 29, 29, 4, 9])[0], 0))

        elif new_biome == 'bog':
            self.platforms.append(Platform('bog', None, (0, -1400), images['transition3'], 0))

            for i in range(8):
                if random.randint(0, 1) == 0: x = random.randint(0, 100)
                else: x = random.randint(250, 500)
                y = i*120-1400
                self.platforms.append(Platform('bog', [100, 20], [x, y], images['log2'], 0))

            for i in range(1, 3):
                x = random.randint(150, 200)
                y = i*600-2100
                self.platforms.append(Platform('bog', [90, 400], [x, y], images['log1'], 0))
            
            for _ in range(25):
                x = random.randint(0, 520)
                y = random.randint(-400, 960) - 1350
                self.platforms.append(Platform('bog', None, (x, y), random.choice([images['grass'], images['grass'], images['grass'], images['rock']]), 0))
        
        elif new_biome == 'snowy':
            self.platforms.append(Platform('snowy', None, (0, -1400), images['transition2'], 0))
            for _ in range(6):
                x = random.randint(0, 520)
                y = random.randint(-400, 960) - 1350
                self.platforms.append(Platform('snowy', None, (x, y), random.choice([images['rock2'], images['rock1'], images['stick'], images['fstick']]), 0))
        
        elif new_biome == 'beach':
            self.platforms.append(Platform('beach', None, (0, -1400), images['transition4'], 0))
            for _ in range(25):
                x = random.randint(0, 400)
                y = random.randint(-400, 960) - 1350
                self.platforms.append(Platform('beach', None, (x, y), 
                random.choices([images['sand'], images['sand_2'], images['sand_3'], images['sand_dollar'], images['starfish']], weights=[29, 29, 29, 4, 9])[0], 0))

    def update(self, speed, biome, banned):
        for platform in self.platforms[::-1]:
            platform.update(speed, biome, self.platforms, banned)
    
    def render(self, screen, shadows, images):

        # Rendering the decorations first
        for platform in self.platforms:
            if platform.radius == None:
                platform.render(screen, shadows, images)

        for platform in self.platforms:
            if platform.radius != None:
                platform.render(screen, shadows, images)

    def collision_check(self, feet, walkradius, clicked):
        collisions = [[], []]

        for platform in self.platforms:
            platform.collision_check(collisions, feet, walkradius)
        
        if clicked:
            # Randomly falling platforms
            if random.randint(0, 5) == 0:
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