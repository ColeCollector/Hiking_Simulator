import random, math, pygame

def shadow(image, shadowc):
    image = image.convert_alpha()
    imgwidth, imgheight = image.get_size()
    image.lock()

    # Iterate over each pixel
    for x in range(imgwidth):
        for y in range(imgheight):
            color = image.get_at((x, y))
            if color.a != 0:
                image.set_at((x, y), shadowc + (color.a, ))

    # Unlock the surface
    image.unlock()
    return image

def image_variety(images, key):
    original = images[key]
    flipped = pygame.transform.flip(original, True, False)

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

        if self.pos[1] > 960:
            if self.biome == biome and self.img not in banned:
                self.pos[1] = - 400/2
                self.timer = 0
            else: 
                platforms.remove(self)
        
    def render(self, screen, shadows, images):
        if self.timer == 0:
            self.img.set_alpha(256)
            offset = 0

            if self.img in [images['log_1'], pygame.transform.flip(images['log_1'], True, False)]:
                offset = 16

            if self.radius != None:
                if self.img not in shadows:
                    if self.biome == 'boulder':
                        shadows[self.img] = shadow(self.img, (76, 76, 76))
                    else:
                        shadows[self.img] = shadow(self.img, (120, 165, 80))
                        
                screen.blit(shadows[self.img], (self.pos[0] - offset, self.pos[1]+3))
            
            screen.blit(self.img, (self.pos[0] - offset, self.pos[1]))
            
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
            self.platforms.append(Platform('boulder', None, [0, -1400], images['transition_4'], 0))

            for i in range(26):
                x = random.randint(0, 490)
                y = i*50 - 1800
                randomchoice = random.randint(0, 1)
                self.platforms.append(Platform('boulder', ([56, 45][randomchoice]), (x, y), [images['boulder'], images['boulder_2']][randomchoice], 0))

            for _ in range(25):
                x = random.randint(0, 520)
                y = random.randint(-400, 960) - 1350
                
                selected_image = image_variety(images, random.choices(['sand', 'sand_2', 'sand_3', 'sand_dollar', 'starfish'], weights=[29, 29, 29, 4, 9])[0])
                self.platforms.append(Platform('beach', None, (x, y), selected_image, 0))

        elif new_biome == 'bog':
            self.platforms.append(Platform('bog', None, (0, -1400), images['transition_3'], 0))

            for i in range(8):
                if random.randint(0, 1) == 0: x = random.randint(0, 100)
                else: x = random.randint(250, 500)
                y = i*120-1400
                self.platforms.append(Platform('bog', [100, 20], [x, y], image_variety(images, 'log_2'), 0))

            for i in range(1, 3):
                x = random.randint(150, 200)
                y = i*600-2100
                self.platforms.append(Platform('bog', [90, 400], [x, y], image_variety(images, 'log_1'), 0))
            
            for _ in range(45):
                x = random.randint(0, 520)
                y = random.randint(-400, 960) - 1350

                selected_image = image_variety(images, random.choices(['grass', 'shading', 'shading_2', 'shading_3', 'rock'], weights=[3,1,1,1,1])[0])
                self.platforms.append(Platform('bog', None, (x, y), selected_image, 0))
        
        elif new_biome == 'snowy':
            self.platforms.append(Platform('snowy', None, (0, -1400), images['transition_2'], 0))
            for _ in range(6):
                x = random.randint(0, 520)
                y = random.randint(-400, 960) - 1350

                selected_image = image_variety(images, random.choice(['rock_1', 'rock_2', 'stick']))
                self.platforms.append(Platform('snowy', None, (x, y), selected_image, 0))
        
        elif new_biome == 'beach':
            self.platforms.append(Platform('beach', None, (0, -1400), images['transition_4'], 0))
            for _ in range(25):
                x = random.randint(0, 520)
                y = random.randint(-400, 960) - 1350

                selected_image = image_variety(images, random.choices(['sand', 'sand_2', 'sand_3', 'sand_dollar', 'starfish'], weights=[29, 29, 29, 4, 9])[0])
                self.platforms.append(Platform('beach', None, (x, y), selected_image, 0))

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