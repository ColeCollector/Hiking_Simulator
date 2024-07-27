import pygame, random, math

height = 800
width = 450

# pygame setup
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

invitems = {"Water" : ["plastic bottle","metal bottle", "water jug"],"Sleeping Bag":["light bag(10C)","3 season bag(-5C)","winter bag(-40)"], "Left Foot":["crocs","hiking boots","work boots"],"Right Foot":["crocs","hiking boots","work boots"],"Locked_1" : None,"Locked_2" : None, "Clothes":["no spare clothes","an extra of everything","7 days of clothes"]}
invitems = list(invitems.keys())

images = {
'log1' : pygame.image.load('images/log_1.png'),
'log2' : pygame.image.load('images/log_2.png'),
'rock' : pygame.image.load('images/rock.png'),
'rock1' : pygame.image.load('images/rock_1.png'),
'rock2' : pygame.image.load('images/rock_2.png'),
'big_boulder' : pygame.image.load('images/big_boulder.png'),
'stick' : pygame.image.load('images/stick.png'),
'fstick' : pygame.transform.flip(pygame.image.load('images/stick.png'), True, False),

'grass' : pygame.image.load('images/grass.png'),
'fire' : pygame.image.load('images/fire.png'),
'bolt' : pygame.image.load('images/bolt.png'),

'sand' : pygame.image.load('images/sand.png'),
'sand_2' : pygame.image.load('images/sand_2.png'),
'sand_3' : pygame.image.load('images/sand_3.png'),
'sand_dollar' : pygame.image.load('images/sand_dollar.png'),

'boulder' : pygame.image.load('images/boulder.png'),
'boulder2' : pygame.image.load('images/boulder_2.png'),
'fboulder' : pygame.transform.flip(pygame.image.load('images/boulder.png'), True, False),

'transition1' : pygame.image.load('images/transition_1.png'),
'transition2' : pygame.image.load('images/transition_2.png'),
'transition3' : pygame.image.load('images/transition_3.png'),
'transition4' : pygame.image.load('images/transition_4.png'),
'backpack' : pygame.image.load('images/backpack.png'),
'perks' : pygame.image.load('images/perks.png')
}

normal = [pygame.transform.flip(pygame.image.load('images/foot.png'), True, False),pygame.image.load('images/foot.png')]

def shadow(image,shadowc):
    image = image.convert_alpha()
    imgwidth, imgheight = image.get_size()
    image.lock()

    # Iterate over each pixel
    for x in range(imgwidth):
        for y in range(imgheight):
            color = image.get_at((x, y))
            if color.a != 0:
                image.set_at((x, y), shadowc + (color.a,))

    # Unlock the surface
    image.unlock()
    return image

shadows = {
    images['log1'] : shadow(images['log1'],(120, 165, 80)),
    images['log2'] : shadow(images['log2'],(120, 165, 80)),
    images['boulder'] : shadow(images['boulder'],(76,76,76)),
    images['fboulder'] : shadow(images['fboulder'],(76,76,76)),
    images['boulder2'] : shadow(images['boulder2'],(76,76,76)),
    images['big_boulder'] : shadow(images['big_boulder'],(76,76,76))
    }


stamina = 400
heat = 150
hoptime = 0
score = 0
locked = -1
walkradius = [80,80]
scale = 0
counter = 0

jumps = 0
effects = {
    'slipchance' : 0,
    'heat'       : 0.05,
    'stamina'    : 0.05
}

platforms = []
decoration = []
footprints = []
obstacles = []

stats = {
'Water'        : 'Stamina will refill faster',
'Matress'      : 'WIP',
'Sleeping Bag' : 'Lets you skip night time',
'Left Foot'    : ['Upgrades left footwear','Lets you walk further'],
'Right Foot'   : ['Upgrades right footwear','Lets you walk further'],
'Clothes'      : 'Protection from heat'
}




running = True
clicked = False
menu = True
ignore = False
twisted = False


#fuck you I did something
print("penisssss")
bgcolor = "gray"

feet = [[width/2-100,700],[width/2+100,700]]

#backround audio
pygame.mixer.music.load('sounds/ambience.wav')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.05)

sounds = [pygame.mixer.Sound('sounds/ow.wav'),pygame.mixer.Sound('sounds/jump.wav'),pygame.mixer.Sound('sounds/bone.mp3')]
sounds[0].set_volume(0.1)
sounds[1].set_volume(0.2)

#this is so that rectangles and circles can be stored in the same list
#(sorry for bad explanation)
class Hitbox:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

# Function to check if rectangles are intersecting with circles
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

# Function to check for the closest point to a point on a circle
def closest_point_on_circle(pos, center, radius):
    dx = pos[0] - center[0]
    dy = pos[1] - center[1]
    distance = math.sqrt(dx * dx + dy * dy)
    ratio = radius / distance
    closest_x = center[0] + dx * ratio
    closest_y = center[1] + dy * ratio
    return [closest_x, closest_y]

# Function to check if a point is in a circle
def is_within_circle(pos, center, radius):
    dx = pos[0] - center[0]
    dy = pos[1] - center[1]
    return dx * dx + dy * dy < radius * radius

# Function to check if the foot is in the circle and it pushes it out
def no_no_circle(pos):
    for obstacle in obstacles:
        hitbox = obstacle['hitbox']
        if is_within_circle(pos, (hitbox.x,hitbox.y), hitbox.r):
            pos = closest_point_on_circle(pos, (hitbox.x,hitbox.y),hitbox.r)
    return pos

# Function to check for circles intersecting with each other
def circles_intersect(circle1_pos, circle1_radius, circle2_pos, circle2_radius):
    # Calculate the distance between the centers of the circles
    distance = math.sqrt((circle1_pos[0] - circle2_pos[0])**2 + (circle1_pos[1] - circle2_pos[1])**2)

    # Check if the distance is less than the sum of the radii
    if distance < circle1_radius + circle2_radius:
        return True
    else:
        return False

# Function to display text on the screen
def show_text(text,size,location,color):
    a1 = pygame.font.Font(None, size).render(text, True, color)
    a2 = a1.get_rect(center=location) 
    screen.blit(a1, a2)

# Function to convert from hex color to rgb color
def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

# Function to make the screen red 
def damage_tint(surface, scale):
    a = min(255, max(0, round(255 * (1-scale))))
    surface.fill((255, a, a), special_flags = pygame.BLEND_MIN)

# Function to switch to boulder biome  
def biomeboulder():
    global biome, platforms, obstacles
    biome = 'boulder'

    obstacles.append({
    "hitbox" : Hitbox(100, 500 - 1350, 200),
    "img" : images['big_boulder'],
    "biome" : "boulder",
    })

    #generating new platforms
    for i in range(26):
        platform_x = random.randint(100,400)
        platform_y = i*50 - 1800
        randomchoice = random.randint(0,2)
        
        platforms.append({
            "hitbox" : Hitbox(platform_x, platform_y,[56,56,45][randomchoice]),
            "img" : [images['boulder'],images['fboulder'],images['boulder2']][randomchoice],
            "biome" : "boulder",
            "timer" : 0
            })
        
    decoration.append({
        "hitbox" : pygame.Rect(0, -1400, 0, 0),
        "img" : images['transition1'],  
        "biome" : "boulder"
        }) 

# Function to switch to snowy biome  
def biomesnowy():
    global biome,footprints
    biome = 'snowy'
    footprints = []  

    decoration.append({
        "hitbox" : pygame.Rect(0, -1400, 0, 0),
        "img" : images['transition2'],
        "biome" : "snowy"
        }) 
    
    for _ in range(6):
        platform_x = random.randint(0,400)
        platform_y = random.randint(-400,800) - 1350
        decoration.append({
            "hitbox" : pygame.Rect(platform_x, platform_y, 0, 0),
            "img" : random.choice([images['rock2'],images['rock1'],images['stick'],images['fstick']]),
            "biome" : "snowy"
            })    

# Function to switch to log biome    
def biomelog():
    global biome,platforms
    biome = 'log'
    #-500
    # platforms properties
    platform_width = 100
    platform_height = 20

    for i in range(8):
        if random.randint(0,1) == 0: platform_x = random.randint(0,100)
        else: platform_x = random.randint(300,400)
            
        platform_y = i*120-1400
        platforms.append({
            "hitbox" : pygame.Rect(platform_x, platform_y, platform_width, platform_height),
            "img" : images['log2'],
            "biome" : "log"
            })

    platform_height = 400
    platform_width = 90

    for i in range(1,3):
        platform_x = random.randint(100,300)
        platform_y = i*600-2100
        platforms.append({
            "hitbox" : pygame.Rect(platform_x, platform_y, platform_width, platform_height),
            "img" : images['log1'],
            "biome" : "log"
            })
        
    decoration.append({
        "hitbox" : pygame.Rect(0, -1400, 0, 0),
        "img" : images['transition3'],
        "biome" : "log"
        }) 
    
    for _ in range(25):
        platform_x = random.randint(0,400)
        platform_y = random.randint(-400,800) - 1350
        decoration.append({
            "hitbox" : pygame.Rect(platform_x, platform_y, 0, 0),
            "img" : random.choice([images['grass'],images['grass'],images['grass'],images['rock']]),
            "biome" : "log"
            })    

def biomebeach():
    global biome
    biome = 'beach'

    decoration.append({
        "hitbox" : pygame.Rect(0, -1400, 0, 0),
        "img" : images['transition4'],  
        "biome" : "beach"
        }) 
    
    for i in range(2):
        platform_x = 0
        platform_y = i*800 - 2100
        platforms.append({
            "hitbox" : pygame.Rect(platform_x, platform_y, 0, 0),
            "img" : [pygame.image.load('images/beach_1.png'),pygame.image.load('images/beach_2.png'),pygame.image.load('images/beach_3.png'),pygame.image.load('images/beach_2.png')],
            "biome" : "beach"
            })    

    for _ in range(25):
        platform_x = random.randint(0,400)
        platform_y = random.randint(-400,800) - 1350
        decoration.append({
            "hitbox" : pygame.Rect(platform_x, platform_y, 0, 0),
            "img" : random.choices([images['sand'],images['sand_2'],images['sand_3'],images['sand_dollar']],weights=[32,32,32,4])[0],
            "biome" : "beach"
            })     
        
# Function to calculate the vertices of a hexagon
def calculate_hexagon_vertices(center, size):
    return [
        (center[0] + size * math.cos(math.radians(60 * i)), 
         center[1] + size * math.sin(math.radians(60 * i)))
        for i in range(6)
    ]

# Function to check if a point is inside a polygon
def point_in_polygon(point, vertices):
    x, y = point
    n = len(vertices)
    inside = False
    p1x, p1y = vertices[0]
    for i in range(n + 1):
        p2x, p2y = vertices[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

# Define colors
bg_color = '#0B1911'
hexagon_default_color = '#304D30'
hexagon_hover_color = '#387738'
hexagon_selected_color = '#EEF0E5'
hexagon_outline_color = '#163020'

# Hexagon properties
hexagons = []
selected = []

for i in range(2):
    vertices = calculate_hexagon_vertices((i*180+135,347),60)
    hexagons.append(vertices)

for i in range(2):
    vertices = calculate_hexagon_vertices((i*180+135,450),60)
    hexagons.append(vertices)

for i in range(3):
    vertices = calculate_hexagon_vertices((225,296+103*i),60)
    hexagons.append(vertices)


def menu_start():
    global menu
    screen.fill(bg_color)
    
    #screen.blit(images['backpack'],(30,100))
    show_text("PICK TWO",60,(width/2, height/2-250), "white")
    show_text("ITEMS",60,(width/2, height/2-200), "white")

    for hexagon in hexagons:
        if hexagons.index(hexagon) in selected:
            color = hexagon_selected_color
            if clicked == True and point_in_polygon(pos, hexagon):
                selected.remove(hexagons.index(hexagon))
            
        elif point_in_polygon(pos, hexagon):
            if clicked == True and len(selected) < 2:
                selected.append(hexagons.index(hexagon))
            color = hexagon_hover_color

        else: color = hexagon_default_color 

        # Displaying Hexagons
        pygame.draw.polygon(screen, color, hexagon, 0)
        pygame.draw.polygon(screen, hexagon_outline_color, hexagon, 8)
    
    
    if  pygame.Rect(width/2-100,585,200,50).collidepoint(pos):
        pygame.draw.rect(screen, hexagon_hover_color, (width/2-100,585,200,50))
        if clicked == True and len(selected) == 2:
            menu = False
            # Finding which perk based on which hexagon was selected
            perks = invitems[selected[0]],invitems[selected[1]]

            # Applying the perks
            for perk in perks:
                if perk == 'Left Foot':
                    walkradius[0] += 5
                    normal[0] = pygame.transform.flip(pygame.image.load('images/boot.png'), True, False)

                elif perk == 'Right Foot':
                    walkradius[1] += 8
                    normal[1] = pygame.image.load('images/croc.png')
                    effects['slipchance'] += 1

                elif perk == 'Water':
                    effects['stamina'] -= 0.01

                elif perk == 'Clothes':
                    effects['heat'] -= 0.02

                elif perk == 'Sleeping Bag':
                    pass

            shadows[normal[0]] = shadow(normal[0],(22,22,22))
            shadows[normal[1]] = shadow(normal[1],(22,22,22))
        
    else:
        pygame.draw.rect(screen, hexagon_default_color, (width/2-100,585,200,50))
    show_text('DONE',50,(width/2,610),'white')

    screen.blit(images['perks'],(0, -60))

def bg_color_switch():
    global bgcolor, platforms

    if biome == 'boulder':
        #changing the bg after the transition has past
        if bgcolor != '#A0A0A0' and (score/50 > lastbiomeswitch + 25):
            bgcolor = '#A0A0A0'

        # Randomly falling boulders


        if random.randint(0,5-effects['slipchance']) == 0:
            ontop = [j for sublist in collisions for j, value in enumerate(sublist) if value]
            
            # If we are ontop of a boulder
            if len(ontop) != 0:
                randplatform = random.choice(ontop)
                if platforms[randplatform]['biome'] == 'boulder' and platforms[randplatform]['timer'] == 0:
                    platforms[randplatform]['timer'] = 180

    elif biome == 'snowy':
        #changing the bg after the transition has past
        if bgcolor != '#FFFFFF' and (score/50 > lastbiomeswitch + 25):
            bgcolor = '#FFFFFF'

    elif biome == 'log':
        #changing the bg after the transition has past
        if bgcolor != '#A8CA59' and (score/50 > lastbiomeswitch + 25):
            bgcolor = '#A8CA59'

    elif biome == 'beach':
        #changing the bg after the transition has past
        if bgcolor != '#FDE9BE' and (score/50 > lastbiomeswitch + 25):
            bgcolor = '#FDE9BE'

# Starting with log biome
biomebeach()
biomeswitch = random.randint(40,60)
lastbiomeswitch = 0
lastbiome = None

while running:
    pos = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()

    # Check if we are in the menu
    if mouse_buttons[0] and menu == False:
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
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 :
            clicked = True

            # Check if we are in the menu
            if menu == False:
                sounds[1].play()
                # Moving faster if at least one foot is high up
                hoptime = (780-max(feet[0][1],feet[1][1]))/15+7
                jumps += 1
                
                # Switching the bg color
                bg_color_switch()

                # If a foot is locked
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

    
    # Choosing items before the game starts
    if menu == True:
        menu_start()
        
   
    else:
        if lastbiomeswitch+20 > score/50:
            current_biome = lastbiome
        else:
            current_biome = biome

        # Switching biomes
        if score/50 > biomeswitch:
            lastbiome = biome

            # Chooses a random biome (other than the currentbiome)
            if biome == 'log':
                randombiome = random.choice([biomeboulder,biomesnowy,biomebeach])

            elif biome == 'boulder':
                randombiome = random.choice([biomelog,biomesnowy,biomebeach])

            elif biome == 'snowy':
                randombiome = random.choice([biomeboulder,biomelog,biomebeach])

            elif biome == 'beach':
                randombiome = random.choice([biomeboulder,biomelog,biomesnowy])

            randombiome()
            
            lastbiomeswitch = biomeswitch
            biomeswitch += random.randint(40,60)
            

        # Moving the platforms when we move:
        if hoptime > 0:
            hoptime -= hoptime/3
            if hoptime < 0.1:hoptime = 0

            for platform in platforms:
                platform['hitbox'].y+=hoptime

            for obstacle in obstacles:
                obstacle['hitbox'].y+=hoptime

            for decor in decoration:
                decor['hitbox'].y+=hoptime

            for foot in feet:
                foot[1] += hoptime

            for footprint in footprints:
                footprint[1][1] += hoptime

            score+=hoptime

        # Fill the screen with a color to wipe away anything from last frame
        screen.fill(bgcolor)
        
        for decor in decoration:
            screen.blit(decor['img'],(decor['hitbox'].x,decor['hitbox'].y))
            # Removing decorations if they hit the bottom and it isn't their biome
            
            if decor['hitbox'].y > 800:
                decor['hitbox'].y = -400
                if biome != decor['biome'] or decor['img'] in [images['transition1'],images['transition2']]:
                    decoration.remove(decor)

        for footprint in footprints:
            screen.blit(footprint[0],footprint[1])

        collisions = [[],[]]
        for platform in platforms[:]:
            hitbox = platform['hitbox']


            if platform['biome'] == 'log':

                if platform["img"] == images['log2']:
                    # Checking/printing the ladder steps 
                    screen.blit(shadows[platform['img']],(hitbox.x,hitbox.y+6))
                    screen.blit(platform['img'],(hitbox.x,hitbox.y))

                elif platform["img"] == images['log1']:
                    # Checking/printing the tall logs
                    screen.blit(shadows[platform['img']],(hitbox.x-33,hitbox.y+6))
                    screen.blit(platform['img'],(hitbox.x-33,hitbox.y))

                collisions[0].append(rect_circle_intersect(hitbox, feet[0], walkradius[0]*0.8))
                collisions[1].append(rect_circle_intersect(hitbox, feet[1], walkradius[1]*0.8))

            elif platform['biome'] == 'beach':
                counter += 1
                if counter == 240:
                    counter = 0

                screen.blit(platform['img'][round(counter/60-1)], (hitbox.x,hitbox.y))

            else:
                # Checking/printing the boulders
                if platform['timer'] == 0:
                    platform['img'].set_alpha(256)
                    screen.blit(shadows[platform['img']],(hitbox.x-hitbox.r,hitbox.y+6-hitbox.r))
                    screen.blit(platform['img'],(hitbox.x-hitbox.r,hitbox.y-hitbox.r))
                    #pygame.draw.circle(screen,"green",[hitbox.x,hitbox.y],hitbox.r)
                    collisions[0].append(circles_intersect(feet[0], walkradius[0]*0.8,[hitbox.x,hitbox.y],hitbox.r))
                    collisions[1].append(circles_intersect(feet[1], walkradius[1]*0.8,[hitbox.x,hitbox.y],hitbox.r))

                else:
                    # Setting boulder opacity to the amount of time before they reappear
                    platform['img'].set_alpha(platform['timer'])
                    screen.blit(platform['img'],(hitbox.x-hitbox.r,hitbox.y-hitbox.r))
                    platform['timer'] -= 1

            # Reset objects when the hit the bottom

            # Boulders are bigger so they reset before the other shit
            if platform['biome'] == 'boulder': 

                # Moving platforms back to the top
                if platform['hitbox'].y > 1000:
                    platform['hitbox'].x = random.randint(100,400)
                    platform['hitbox'].y = -400
                    platform['timer'] = 0

                    # Remove the platform if it's not in their own biome
                    if biome != 'boulder':
                        platforms.remove(platform)

            elif platform['hitbox'].y > 800:
                # Remove the platform if it's not in their own biome 
                if biome != platform['biome']:
                    platforms.remove(platform)

                elif platform["img"] == images['log2']:
                    if random.randint(0,1) == 0: platform['hitbox'].x = random.randint(0,100)
                    else: platform['hitbox'].x = random.randint(300,400)

                elif platform["img"] == images['log1']:
                    platform['hitbox'].x = random.randint(100,300)
                

                # Moving platforms back to the top
                platform['hitbox'].y = -400
                if platform['biome'] == 'beach':
                    platform['hitbox'].y = 0

        for obstacle in obstacles[:]:
            hitbox = obstacle['hitbox']

            if obstacle['biome'] == 'boulder': 
                if obstacle['hitbox'].y > 1000:
                    obstacle['hitbox'].x = 350
                    obstacle['hitbox'].y = -400
                    if biome != 'boulder':
                        obstacles.remove(obstacle)

            #pygame.draw.circle(screen,"red",[hitbox.x,hitbox.y],hitbox.r,12)

            #screen.blit(shadows[obstacle['img']],(hitbox.x-hitbox.r,hitbox.y+4-hitbox.r))
            screen.blit(obstacle['img'],(hitbox.x-hitbox.r,hitbox.y-hitbox.r))



        for foot in feet:
            screen.blit(normal[feet.index(foot)], (foot[0]-75,foot[1]-75))
            if True not in collisions[feet.index(foot)] and score != 0:

                if current_biome == 'snowy':
                    if scale == 0:
                        # Adds footprints and a longer delay for being hurt for falling if we are in the snowy biome
                        footprints.append([shadows[normal[1]], [feet[1][0]-75,feet[1][1]-75]])
                        footprints.append([shadows[normal[0]], [feet[0][0]-75,feet[0][1]-75]])
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
                #regeneration
                stamina += effects['stamina']

        if current_biome != 'snowy' : 
            if heat > 150:
                heat -= effects['heat']
                
            elif heat < 150:
                heat += effects['heat']


        #if twisted: 
        #    #make the text fade away from the screen at some point future me
        #    if scale!=0:
        #       show_text('Twisted Ankle',90,(width/2+5,height/2+5),'black')
        #        show_text('Twisted Ankle',90,(width/2,height/2),'white')

        if scale != 0:
            #red screen
            if current_biome == 'snowy':
                damage_tint(screen,scale/200)
            else:
                damage_tint(screen,scale/100)

            #making it fade away
            scale -= 2

        for i in range(2):
            pygame.draw.circle(screen,"white",feet[i],walkradius[i]+1,1)

        pygame.draw.circle(screen,"red",pos,15)
        
        #stamina bar
        pygame.draw.rect(screen, "darkblue", (width/2-152,68,304,24))
        pygame.draw.rect(screen, "blue", (width/2-150,70,stamina,20))
        screen.blit(images['bolt'], (width/2-170,58))

        #heat bar
        pygame.draw.rect(screen, "red", (width/2-152,100,304,24))
        pygame.draw.rect(screen, "orange", (width/2-150,102,heat,20))
        screen.blit(images['fire'], (width/2+130,90))

        #displaying score
        show_text(str(int(score/50)),74,(width/2,35), "white")

        #displaying biome in bottom right (for testing)
        show_text(str(current_biome),40,(width-40,height-30), "black")

        #you die if you run out of stamina or your feet are off the screen
        if stamina <= 0 or feet[0][1] > height or feet[1][1] > height: 
            print("STATS:")
            print("  Score:",round(score/50,2))
            print("  Jumps:", jumps)
            if stamina <=0:
                print("Cause of death : No Stamina" )
            else:
                print("Cause of death : Feet went off screen" )    
            exit()

        elif heat <=0 or heat >= 300:
            stamina -= effects['stamina']*2


    pygame.display.flip()
    clock.tick(60)  # limits FPS to 60
    clicked = False

pygame.quit()