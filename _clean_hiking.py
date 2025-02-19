import pygame, math, random
from _platforms import Platforms
from _menu import Menu
from _utils import closest_point_on_circle, avoid_obstacles, show_text, damage_tint, shadow

# Initialize Pygame
pygame.init()

# Screen Size
WIDTH, HEIGHT = 540, 960
display = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
screen = pygame.Surface((WIDTH / 2, HEIGHT / 2))
clock = pygame.time.Clock()
pygame.display.set_caption("Hiking Game")

# Backround audio
pygame.mixer.music.load('sounds/ambience.wav')
pygame.mixer.music.set_volume(0.05)
pygame.mixer.music.play(-1)

sounds = [pygame.mixer.Sound('sounds/ow.wav'), pygame.mixer.Sound('sounds/jump.wav'), pygame.mixer.Sound('sounds/bone.mp3'), 
          pygame.mixer.Sound('sounds/splash.mp3'), pygame.mixer.Sound('sounds/snow.mp3')]

sounds[0].set_volume(0.1)
sounds[1].set_volume(0.2)
sounds[2].set_volume(0.5)
sounds[3].set_volume(0.1)
sounds[4].set_volume(0.1)

images = {'bar'       : pygame.image.load(f'images/UI/bar.png'),
          'highscore' : pygame.image.load(f'images/UI/highscore.png'),
          'foot_1'    : pygame.transform.flip(pygame.image.load('images/shoes/foot.png'), True, False),
          'foot_2'    : pygame.image.load(f'images/shoes/foot.png')}

feet = [[85, 350], [185, 350]]

walkradius = [40, 40] 
selected = -1
highscore = 0
speed = 0 
score = 0
scale = 0
wet_feet = 0
temp = 150
stamina = 300
clicking = False

transition = -70
dead = 0

game_status = 'menu'

# Starting bome
biome = 'boulder'
biomeswitch = random.randint(25, 40)
lastbiomeswitch = 0
lastbiome = None
feetdistance = 0

platforms = []
platforms = Platforms(platforms, biome)

colors = {'bog':'#ACC16A', 'boulder':'#158BA5', 'snowy':'#E4FFFF', 'beach':'#FDE9BE', 'ladder' : '#282828'}
bgcolor = "gray"

# Snowflake properties
snowflakes = []
for _ in range(150):  # Number of snowflakes
    x = random.randint(0, WIDTH + 500)
    y = random.randint(-200, 0)
    speed = random.randint(2, 4)
    size = random.randint(2, 4)
    angle = random.randint(2, 4)
    snowflakes.append([x, y, speed, size, angle])

running = True

while running:
    # Get mouse position and scale it down
    pos = list(pygame.mouse.get_pos())
    pos[0] /= 2
    pos[1] /= 2

    mouse_buttons = pygame.mouse.get_pressed()
    
    if game_status == 'game' and mouse_buttons[0]:  # If left mouse button is pressed
        if selected != -1:  # If not foot is selected
            pos = avoid_obstacles(closest_point_on_circle(pos, feet[selected], walkradius[selected]), obstacles, selected)

        else:  # If a foot is selected
            distances = [math.hypot(pos[0] - foot[0], pos[1] - foot[1]) for foot in feet]
            if all(dist > walkradius[i] for i, dist in enumerate(distances)):
                selected = distances.index(min(distances))
                pos = closest_point_on_circle(pos, feet[selected], walkradius[selected])
            pos = avoid_obstacles(pos, obstacles, selected)

    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # If the user closes the window
            running = False

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # If the left mouse button is released
            clicking = True

            if game_status == 'game' and mouse_buttons[0]:

                sounds[1 if current_biome != 'snowy' else 4].play()
                speed = (450 - max(feet[0][1], feet[1][1])) / 15

                selected = -1  # Unselect the foot
                feetdistance = math.sqrt((feet[1][0]-feet[0][0])**2 + (feet[1][1]-feet[0][1])**2)
                feet[distances.index(min(distances))] = list(pos)

    if game_status == 'menu':
        menu = Menu(screen, clicking, pos, walkradius, [images['foot_1'], images['foot_2']])

        # Get the statistics chosen from menu
        images['foot_1'] = menu.normal[0]
        images['foot_2'] = menu.normal[1]
        game_status = menu.game_status
        effects = menu.effects

    elif game_status == 'game':
        # Changing the bg after the transition has past
        if bgcolor != colors[biome] and (score / 50 > lastbiomeswitch + 14):
            bgcolor = colors[biome]

        current_biome = lastbiome if lastbiomeswitch + 10 > score / 50 else biome

        # Switching biomes
        if score / 50 > biomeswitch:
            lastbiome = biome
            
            # Chooses a random biome (other than the currentbiome)
            biomes = list(colors.keys())
            biomes.remove(biome)
            biome = random.choice(biomes)

            platforms = Platforms(platforms, biome)

            lastbiomeswitch = biomeswitch
            biomeswitch += random.randint(25, 40)

        # Fill the screen with a color
        screen.fill(bgcolor)

        # Giving a speed to all the objects so they move
        speed -= speed / 3
        if speed < 0.1: speed = 0

        score += speed

        platforms.update(round(speed), biome)
        platforms.render(screen)  
        platforms.collision_check(feet, walkradius, clicking, effects['slipchance'])
        obstacles = platforms.obstacles
        collisions = platforms.collisions

        for i, foot in enumerate(feet):
            foot[1] += round(speed)
            pygame.draw.circle(screen, pygame.Color("white"), foot, walkradius[i] + 1, 1)
            screen.blit(images[f'foot_{i + 1}'], (foot[0] - 38, foot[1] - 38))

        p1, p2 = feet[0], feet[1]
        r1, r2 = walkradius[0] + 1, walkradius[1] + 1  # Account for outline radius

        # Compute the direction vector
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        dist = math.sqrt(dx**2 + dy**2)

        if dist > sum(walkradius):  # Avoid division by zero
            # Normalize the vector
            dx /= dist
            dy /= dist

            # Compute edge points
            edge1 = (p1[0] + dx * r1, p1[1] + dy * r1)
            edge2 = (p2[0] - dx * r2, p2[1] - dy * r2)

            # Draw the line
            pygame.draw.line(screen, pygame.Color("white"), edge1, edge2, 1)

        for tree in platforms.trees:
            screen.blit(tree[0],tree[1])
        
        # If feet are too far apart or left foot isnt on the left
        if scale == 0:
            if feet[0][0] > feet[1][0] or 180 < feetdistance:
                sounds[2].play()
                scale = 100
                stamina -= effects['stamina'] * 300
        
            # If we are not on any platform
            elif (not any(collisions[0]) or not any(collisions[1])) and current_biome not in ['beach', None]:
                if current_biome == 'snowy':
                    # Add footprints and increase hurt delay in snowy biome
                    platforms.footprint(platforms, [(feet[0][0] - 38) * 2, (feet[0][1] - 38) * 2], shadow(images['foot_1'], (160, 160, 160)))
                    platforms.footprint(platforms, [(feet[1][0] - 38) * 2, (feet[1][1] - 38) * 2], shadow(images['foot_2'], (160, 160, 160)))
                    scale = 200
                    stamina -= effects['stamina'] * 100
                else:
                    scale = 100
                    stamina -= effects['stamina'] * 500

                sounds[0].play()
                if current_biome == 'boulder':
                    sounds[3].play()
                    wet_feet = 480
                    effects['temp'] -= 30

        # Regeneration
        elif stamina < 300 and current_biome != 'snowy':
            stamina += effects['regen']

        if current_biome == 'beach':
            temp += 0.05

        elif current_biome == 'snowy':
            temp -= 0.05
            stamina -= effects['stamina'] * 4

            # Update and draw snowflakes
            for flake in snowflakes:
                flake[0] -= flake[2] * (flake[3] / 2)
                flake[1] += flake[2]
                if flake[1] > HEIGHT or flake[0] < 0:
                    flake[0] = random.randint(0, WIDTH + 500)
                    flake[1] = random.randint(-20, -5)

                pygame.draw.circle(screen, 'white', (flake[0], flake[1]), flake[3])
        
        else:
            # Bringing temp level back to middle
            if temp > 150: 
                temp -= min(0.025, temp - 150)

            elif temp < 150:
                temp += 0.025

        if scale != 0:
            # Apply and slowly fade damage tint
            damage_tint(screen, scale / (200 if current_biome == 'snowy' else 100))
            scale -= 1

        # Mouse Position Circle
        pygame.draw.circle(screen, 'white', pos, 10, 1)
        pygame.draw.circle(screen, 'white', pos, 2)
        
        # Stamina bar
        pygame.draw.rect(screen, "#133672", (59, 44, 152, 12))
        pygame.draw.rect(screen, "#2B95FF", (60, 45, stamina / 2, 10))

        # Temperature bar
        pygame.draw.rect(screen, "#AFAFAF", (59, 64, 152, 12))
        pygame.draw.rect(screen, "#E00000", (60, 65, (temp + effects['temp']) / 2, 10))
        screen.blit(images['bar'], (36, 39))

        #-100 to 100 degrees celcius
        show_text(screen, f"{str(round((temp + effects['temp'] - 150) / 3))}°C", (113, 86), "white")

        # Displaying biome in bottom right (for testing)
        show_text(screen, str(current_biome), (245, 465), "black")
        
        screen.blit(images['highscore'], (2, 14))

        # Outlined Highscore text
        show_text(screen, str(highscore), (28, 23), 'black')
        show_text(screen, str(highscore), (30, 23), 'black')
        show_text(screen, str(highscore), (28, 21), 'black')
        show_text(screen, str(highscore), (30, 21), 'black')
        show_text(screen, str(highscore), (29, 22), 'white')

        # Displaying score
        show_text(screen, str(int(score / 50)), (137, 24), "black", 32)
        show_text(screen, str(int(score / 50)), (135, 22), "white", 32)

        # Wet Feet
        if wet_feet != 0:
            wet_feet -= 1
            if wet_feet == 0: effects['temp'] += 30
            show_text(screen, "Wet Feet", (80, 106), '#3696BC')
            show_text(screen, "Wet Feet", (80, 105), '#3ED1DC')

        # You die if you run out of stamina
        if stamina <= 0 or transition == 70:   
            transition = min(70, transition + 1)
            dead += 1

        # You take damage if temp is too low or high
        elif temp + effects['temp'] <= 0 or temp + effects['temp'] >= 300:
            stamina -= effects['stamina'] * 2
        
        if transition < 0:
            transition += 1

        if dead:
            if dead >= 10:
                transition = min(70, transition + 1)

            if dead > 80:
                # Resetting everything
                dead = 0
                stamina = 300
                temp = 150
                if wet_feet != 0: effects['temp'] += 30
                wet_feet = 0
                feet = [[85, 350], [185, 350]]

                bgcolor = "gray"

                if highscore < score:
                    highscore = round(score / 50)

                score = 0
                transition = -70
                
                biomes = list(colors.keys())
                biome = random.choice(biomes)
                
                biomeswitch = random.randint(25, 40)
                lastbiomeswitch = 0
                lastbiome = None
                
                platforms = []
                platforms = Platforms(platforms, biome)

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