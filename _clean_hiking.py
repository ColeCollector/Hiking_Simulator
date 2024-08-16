import pygame, math, random
from _platforms import Platforms
from _menu import Menu
import os

# Initialize Pygame
pygame.init()

# Screen Size
WIDTH, HEIGHT = 540, 960
display = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
screen = pygame.Surface((WIDTH/2, HEIGHT/2))
clock = pygame.time.Clock()
pygame.display.set_caption("Hiking Game")

# Backround audio
pygame.mixer.music.load('sounds/ambience.wav')
pygame.mixer.music.set_volume(0.05)
pygame.mixer.music.play(-1)

sounds = [pygame.mixer.Sound('sounds/ow.wav'), pygame.mixer.Sound('sounds/jump.wav'), pygame.mixer.Sound('sounds/bone.mp3')]
sounds[0].set_volume(0.1)
sounds[1].set_volume(0.2)

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

# Get a list of file names
files = os.listdir('images')
images = {}

for file in files: images[file.replace('.png', '')] = pygame.image.load(f'images/{file}')
images['shading_3'] = shadow(pygame.image.load('images/shading_2.png'), (143, 165, 120)) 

for image in images.copy():
    images[f"{image}_flipped"] = pygame.transform.flip(images[image], True, False)

shadows = {
    images['log_1'] : shadow(images['log_1'], (120, 165, 80)), 
    images['log_2'] : shadow(images['log_2'], (120, 165, 80)), 
    images['boulder'] : shadow(images['boulder'], (2, 166, 255)), 
    images['boulder_2'] : shadow(images['boulder_2'], (2, 166, 255)), 
    }

def closest_point_on_circle(pos, center, radius):
    dx = pos[0] - center[0]
    dy = pos[1] - center[1]
    distance = math.sqrt(dx * dx + dy * dy)
    ratio = radius / distance
    closest_x = center[0] + dx * ratio
    closest_y = center[1] + dy * ratio
    return [closest_x, closest_y]

def is_within_circle(pos, center, radius):
    dx = pos[0] - center[0]
    dy = pos[1] - center[1]
    return dx * dx + dy * dy < radius * radius

def no_no_circle(pos):
    for obstacle in obstacles:
        if is_within_circle(pos, (obstacle[0] + 80, obstacle[1] + 80), 80):
            pos = closest_point_on_circle(pos, (obstacle[0] + 80, obstacle[1] + 80), 80)
    return pos

def show_text(text, size, location, color):
    size = round(size*0.65)
    font = pygame.font.SysFont('segoeuiblack', size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=location)
    screen.blit(text_surface, text_rect)

def damage_tint(surface, scale):
    a = min(255, max(0, round(255 * (1-scale))))
    surface.fill((255, a, a), special_flags = pygame.BLEND_MIN)


normal = [pygame.transform.flip(pygame.image.load('images/foot.png'), True, False), pygame.image.load('images/foot.png')]
feet = [[170/2, 700/2], [370/2, 700/2]]

walkradius = [80/2, 80/2] 
locked = -1

# Define the forbidden circle
#forbidden_center = [250, 400]
#forbidden_radius = 100

highscore = 0
speed = 0 
score = 0
scale = 0
dead = 0

transition = -70
heat = 150
stamina = 300

clicking = False
twisted = False
game_status = 'menu'

# Starting bome
biome = 'boulder'
biomeswitch = 30/2
lastbiomeswitch = 0
lastbiome = None

platforms = []
platforms = Platforms(platforms, images, biome)

colors = {'bog':'#ACC16A', 'boulder':'#5FD8FF', 'snowy':'#E4FFFF', 'beach':'#FDE9BE'}
bgcolor = "gray"

# Snowflake properties
snowflakes = []
for _ in range(200):  # Number of snowflakes
    x = random.randint(0, WIDTH + 500)
    y = random.randint(-200, 0)
    speed = random.randint(2, 4)
    size = random.randint(2, 4)
    angle = random.randint(2, 4)
    snowflakes.append([x, y, speed, size, angle])

running = True

while running:
    pos = pygame.mouse.get_pos()  # Get current mouse position
    pos = list(pos)
    pos[0]/=2
    pos[1]/=2
    mouse_buttons = pygame.mouse.get_pressed()  # Get mouse button states
    
    if game_status == 'game' and mouse_buttons[0]:  # If left mouse button is pressed
        if locked != -1:  # If a foot is locked
            pos = closest_point_on_circle(pos, feet[locked], walkradius[locked])
            pos = no_no_circle(pos)

        else:  # If no foot is locked
            distances = [math.hypot(pos[0] - foot[0], pos[1] - foot[1]) for foot in feet]
            if all(dist > walkradius[i] for i, dist in enumerate(distances)):
                locked = distances.index(min(distances))
                pos = closest_point_on_circle(pos, feet[locked], walkradius[locked])
                pos = no_no_circle(pos)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # If the user closes the window
            running = False

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # If the left mouse button is released
            clicking = True

            if game_status == 'game':
                sounds[1].play()
                speed = round((450 - max(feet[0][1], feet[1][1]))/15 + 6)
                if locked != -1:  # If a foot is locked
                    pos = no_no_circle(pos)
                    feet[locked] = list(pos)
                else:
                    # Check if the position is within any foot's radius
                    if any(math.hypot(pos[0] - foot[0], pos[1] - foot[1]) <= walkradius[i] for i, foot in enumerate(feet)):
                        for i, foot in enumerate(feet):
                            if math.hypot(pos[0] - foot[0], pos[1] - foot[1]) <= walkradius[i]:
                                pos = no_no_circle(pos)
                                feet[i] = list(pos)
                                break
                    else:  # Move the closest foot if the position is outside all radii
                        pos = no_no_circle(pos)
                        feet[distances.index(min(distances))] = list(pos)
                locked = -1  # Unlock the foot
                feetdistance = math.sqrt((feet[1][0]-feet[0][0])**2 + (feet[1][1]-feet[0][1])**2)

                # If feet are too far apart or left foot isnt on the left
                if feet[0][0] > feet[1][0] or 325 < feetdistance: 
                    twisted = True
                    if scale == 0:
                        scale = 100
                    sounds[2].play()
                    stamina -= effects['stamina']*100
                    
                else:
                    twisted = False

    if game_status == 'menu':
        menu = Menu(screen, clicking, pos, walkradius, normal, images)
        game_status = menu.game_status
        effects = menu.effects
        shadows[normal[0]] = shadow(normal[0], (160, 160, 160))
        shadows[normal[1]] = shadow(normal[1], (160, 160, 160))

    elif game_status == 'game':
        # Changing the bg after the transition has past
        if bgcolor != colors[biome] and (score/50 > lastbiomeswitch + 28/2):
            bgcolor = colors[biome]

        if lastbiomeswitch + 20/2 > score/50:
            current_biome = lastbiome
        else:
            current_biome = biome

        # Switching biomes
        if score/50 > biomeswitch:
            lastbiome = biome
            
            # Chooses a random biome (other than the currentbiome)
            biomes = ['bog', 'boulder', 'snowy', 'beach']
            biomes.remove(biome)
            biome = random.choice(biomes)

            platforms = Platforms(platforms, images, biome)

            lastbiomeswitch = biomeswitch
            biomeswitch += random.randint(30, 40)/2

        # Fill the screen with a color
        screen.fill(bgcolor)

        # Giving a speed to all the objects so they move
        speed -= speed/3
        if speed < 0.1: speed = 0
        score += speed

        platforms.update(speed, biome, [images['transition_2'], images['transition_3'], images['transition_4'], shadows[normal[0]], shadows[normal[1]]])
        platforms.render(screen, shadows, images)  
        platforms.collision_check(feet, walkradius, clicking)
        obstacles = platforms.obstacles
        collisions = platforms.collisions


        for i, foot in enumerate(feet):
            foot[1] += speed
            
            pygame.draw.circle(screen, pygame.Color("white"), foot, walkradius[i] + 1, 1)
            screen.blit(normal[i], (foot[0]-38, foot[1]-38))

            if True not in collisions[i] and current_biome != None:

                if current_biome == 'snowy':
                    if scale == 0:
                        # Adds footprints and a longer delay for being hurt for falling if we are in the snowy biome
                        platforms.footprint(platforms, [(feet[1][0]-38)*2, (feet[1][1]-38)*2], shadows[normal[1]])
                        platforms.footprint(platforms, [(feet[0][0]-38)*2, (feet[0][1]-38)*2], shadows[normal[0]])
                        scale = 200
                        sounds[0].play()

                    stamina -= effects['stamina']/4
                    heat -= effects['heat']/2

                elif current_biome == 'beach':
                    heat += effects['heat']/2
                    stamina -= effects['stamina']/4
                    
                elif scale == 0:
                    scale = 100
                    sounds[0].play()
                    stamina -= effects['stamina']*200
                    
                else:
                    stamina -= effects['stamina']*4
                
            elif twisted:
                stamina -= effects['stamina']*2

            elif stamina < 300:
                # Regeneration
                stamina += effects['stamina']

        if current_biome != 'snowy' : 
            if heat > 150:
                heat -= effects['heat']
                
            elif heat < 150:
                heat += effects['heat']

        else:
            # Update snowflakes
            for flake in snowflakes:
                flake[0] -= flake[2] * (flake[3]/2)
                flake[1] += flake[2]  # Move flake down by its speed
                if flake[1] > HEIGHT or flake[0] < 0:
                    flake[0] = random.randint(0, WIDTH + 500)  # New random x position
                    flake[1] = random.randint(-20, -5)  # Start above the screen

                # Draw the snowflake
                pygame.draw.circle(screen, 'white', (flake[0], flake[1]), flake[3])

        if scale != 0:
            # Red screen
            if current_biome == 'snowy':
                damage_tint(screen, scale/200)
            else:
                damage_tint(screen, scale/100)

            # Fading the red away
            scale -= 2

        # Draw the position circle
        pygame.draw.circle(screen, 'red', pos, 20/2)
        
        # Stamina bar
        pygame.draw.rect(screen, "#133672", (118/2, 68/2+10, 304/2, 24/2))
        pygame.draw.rect(screen, "#2B95FF", (120/2, 70/2+10, stamina/2, 20/2))

        # Heat bar
        pygame.draw.rect(screen, "#AFAFAF", (118/2, 108/2+10, 304/2, 24/2))
        pygame.draw.rect(screen, "#E00000", (120/2, 110/2+10, heat/2, 20/2))
        screen.blit(images['bar'], (72/2, 58/2+10))
        show_text(str(round(heat))+" / 300", 14, (226/2, 152/2+10), "white")
        
        # Displaying biome in bottom right (for testing)
        show_text(str(current_biome), 20, (490/2, 930/2), "black")

        screen.blit(images['highscore'], (2, 14))

        # Outlined Highscore text
        show_text(str(highscore), 20, (28, 23), 'black')
        show_text(str(highscore), 20, (30, 23), 'black')
        show_text(str(highscore), 20, (28, 21), 'black')
        show_text(str(highscore), 20, (30, 21), 'black')
        show_text(str(highscore), 20, (29, 22), 'white')

        # Displaying score
        show_text(str(int(score/50)), 38, (274/2, 39/2+4), "black")
        show_text(str(int(score/50)), 38, (270/2, 35/2+4), "white")

        # You die if you run out of stamina or your feet are off the screen
        if stamina <= 0 or feet[0][1] > HEIGHT/2 or feet[1][1] > HEIGHT/2 or transition == 70:   
            transition = min(70, transition + 1)
            dead += 1

        # You take damage if heat is too low or high
        elif heat <= 0 or heat >= 300:
            stamina -= effects['stamina']*2
        
        if transition < 0:
            transition += 1

        if dead:
            if dead >= 10:
                transition = min(70, transition + 1)

            if dead > 80:
                # Resetting everything
                dead = 0
                stamina = 300
                heat = 150
                feet = [[170/2, 700/2], [370/2, 700/2]]
                bgcolor = "gray"

                if highscore < score:
                    highscore = round(score/50)

                score = 0
                transition = -70
                
                biome = 'bog'
                biomeswitch = 30/2
                lastbiomeswitch = 0
                lastbiome = None
                twisted = False

                platforms = []
                platforms = Platforms(platforms, images, biome)

        # The black circular transition
        transition_surf = pygame.Surface(screen.get_size())
        pygame.draw.circle(transition_surf, (255, 255, 255), (screen.get_width() // 2, screen.get_height() // 2), (70 - abs(transition)) * 8)
        transition_surf.set_colorkey((255, 255, 255))
        screen.blit(transition_surf, (0, 0))

    # Update the display
    display.blit(pygame.transform.scale(screen, display.get_size()), (0, 0))
    pygame.display.flip()
    clock.tick(60)
    clicking = False

# Quit Pygame
pygame.quit()