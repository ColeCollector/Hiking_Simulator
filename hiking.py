import pygame, random, math

height = 800
width = 450

# pygame setup
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

invitems = {"Water" : ["plastic bottle","metal bottle", "water jug"],"Matress":["no matress","inflatable matress","foam cushioned matress"],"Sleeping Bag":["light bag(10C)","3 season bag(-5C)","winter bag(-40)"], "Left Foot":["crocs","hiking boots","work boots"],"Right Foot":["crocs","hiking boots","work boots"], "Clothes":["no spare clothes","an extra of everything","7 days of clothes"]}
invitems = list(invitems.keys())

log1 = pygame.image.load('images/new/log_1.png')
log2 = pygame.image.load('images/new/log_2.png')
rock = pygame.image.load('images/rock.png')
rock1 = pygame.image.load('images/rock1.png')
rock2 = pygame.image.load('images/rock2.png')
stick = pygame.image.load('images/stick.png')
fstick = pygame.transform.flip(stick, True, False)

grass = pygame.image.load('images/grass.png')
fire = pygame.image.load('images/fire.png')
bolt = pygame.image.load('images/bolt.png')

boulder = pygame.image.load('images/boulder.png')
boulder2 = pygame.image.load('images/boulder2.png')
fboulder = pygame.transform.flip(boulder, True, False)

backpack = pygame.image.load('images/backpack.png')
perks = pygame.image.load('images/perks.png')
normal = [pygame.transform.flip(pygame.image.load('images/new/foot.png'), True, False),pygame.image.load('images/new/foot.png')]

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
    log1 : shadow(log1,(120, 165, 80)),
    log2 : shadow(log2,(120, 165, 80)),
    boulder : shadow(boulder,(76,76,76)),
    fboulder : shadow(fboulder,(76,76,76)),
    boulder2 : shadow(boulder2,(76,76,76))
    }




stamina = 3000
heat = 150
hoptime = 0
score = 0
locked = 3
walkradius = [80,80]
scale = 0

jumps = 0
effects = {
    'slipchance' : 0,
    'heat'       : 0.05,
    'stamina'    : 0.2
}

inventory = []
obstacles = []
decoration = []

stats = {
'Water'        : 'Stamina will refill faster',
'Matress'      : 'WIP',
'Sleeping Bag' : 'Lets you skip night time',
'Left Foot'    : ['Upgrades left footwear','Lets you walk further'],
'Right Foot'   : ['Upgrades right footwear','Lets you walk further'],
'Clothes'      : 'Protection from heat'
}


#footprints = []

for collumn in range(2):
    for row in range(3): inventory.append(pygame.Rect((20+(140*row), height/2-140+(200*collumn),130,180)))
#for row in range(2): inventory.append(pygame.Rect((170+(90*row), height/2-50,80,80)))

#inventory.append(pygame.Rect((100+(110), height/2+60,100,100)))

running = True
clicked = False
menu = True
ignore = False
twisted = False


defaultbg = "#A8CA59"
bg = defaultbg
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

def closest_point_on_circle(pos, locked):
    distance = math.sqrt((pos[0] - feet[locked][0])**2 + (pos[1] - feet[locked][1])**2)
    closest_x = feet[locked][0] + walkradius[locked] * (pos[0] - feet[locked][0]) / distance
    closest_y = feet[locked][1] + walkradius[locked] * (pos[1] - feet[locked][1]) / distance

    return [closest_x, closest_y]

def circles_intersect(circle1_pos, circle1_radius, circle2_pos, circle2_radius):
    # Calculate the distance between the centers of the circles
    distance = math.sqrt((circle1_pos[0] - circle2_pos[0])**2 + (circle1_pos[1] - circle2_pos[1])**2)

    # Check if the distance is less than the sum of the radii
    if distance < circle1_radius + circle2_radius:
        return True
    else:
        return False

def showtext(text,size,location,color):
    a1 = pygame.font.Font(None, size).render(text, True, color)
    a2 = a1.get_rect(center=location) 
    screen.blit(a1, a2)

def hex_to_rgb(hex_code):
    """ Convert hex color code to RGB tuple. """
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) for i in (0, 2, 4))

def colourfade(hex_start, hex_end):
    
    start_rgb = hex_to_rgb(hex_start)
    end_rgb = hex_to_rgb(hex_end)
    
    # Calculate intermediate RGB values
    intermediate_rgb = tuple(int(start + (end - start) * 0.05) for start, end in zip(start_rgb, end_rgb))
    
    # Check if intermediate color is close enough to end color
    if all(abs(c1 - c2) <= 30 for c1, c2 in zip(intermediate_rgb, end_rgb)):
        return hex_end
    
    # Convert intermediate RGB back to hex
    intermediate_hex = '#{:02x}{:02x}{:02x}'.format(*intermediate_rgb)
    
    return intermediate_hex

def tintDamage(surface, scale):
    a = min(255, max(0, round(255 * (1-scale))))
    surface.fill((255, a, a), special_flags = pygame.BLEND_MIN)

def biomeboulder():
    global biome, obstacles
    biome = 'boulder'
    #generating new obstacles
    for i in range(20):
        obstacle_x = random.randint(100,400)
        obstacle_y = i*50 - 1400
        randomchoice = random.randint(0,2)

        obstacles.append({
            "hitbox" : Hitbox(obstacle_x, obstacle_y,[112,112,90][randomchoice]),
            "img" : [boulder,fboulder,boulder2][randomchoice],
            "biome" : "boulder",
            "timer" : 0
            })
        
def biomesnowy():
    global biome,footprints
    biome = 'snowy'
    footprints = []  

    for _ in range(6):
        obstacle_x = random.randint(0,400)
        obstacle_y = random.randint(-20,800) - 800
        decoration.append({
            "hitbox" : pygame.Rect(obstacle_x, obstacle_y, 0, 0),
            "img" : random.choice([rock2,rock1,stick,fstick]),
            "biome" : "snowy"
            })    


def biomelog():
    global biome,obstacles
    biome = 'log'

    # Obstacles properties
    obstacle_width = 100
    obstacle_height = 20

    for i in range(8):
        if random.randint(0,1) == 0: obstacle_x = random.randint(0,100)
        else: obstacle_x = random.randint(300,400)
            
        obstacle_y = i*120
        obstacles.append({
            "hitbox" : pygame.Rect(obstacle_x, obstacle_y, obstacle_width, obstacle_height),
            "img" : log2,
            "biome" : "log"
            })

    obstacle_height = 400
    obstacle_width = 90

    for i in range(1,3):
        obstacle_x = random.randint(100,300)
        obstacle_y = i*600-700
        obstacles.append({
            "hitbox" : pygame.Rect(obstacle_x, obstacle_y, obstacle_width, obstacle_height),
            "img" : log1,
            "biome" : "log"
            })

    for _ in range(20):
        obstacle_x = random.randint(0,400)
        obstacle_y = random.randint(-20,800)
        decoration.append({
            "hitbox" : pygame.Rect(obstacle_x, obstacle_y, 0, 0),
            "img" : random.choice([grass,grass,grass,rock]),
            "biome" : "log"
            })    

#starting with log biome
biomelog()
biomeswitch = 10

while running:
    pos = pygame.mouse.get_pos()
    mouse_buttons = pygame.mouse.get_pressed()

    if mouse_buttons[0] and ignore == False:

        if locked != 3:
            pos = closest_point_on_circle(pos,locked)
        else:
            distances = []
            for i in range(2):
                if not (feet[i][0]-pos[0])**2 + (feet[i][1]-pos[1])**2 < walkradius[i]**2:
                    distances.append(math.sqrt((pos[0] - feet[i][0])**2 + (pos[1] - feet[i][1])**2))

            #if the mouse is in one of the circles
            if len(distances) == 2:
                if distances[0] > distances[1]: 
                    pos = closest_point_on_circle(pos,1)
                    locked = 1
                else: 
                    pos = closest_point_on_circle(pos,0)
                    locked = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            ignore = False

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 :
            clicked = True
            #this if statement is here because theres a weird glitch with the
            #starting inventory menu if its not there
            if ignore == False:
                sounds[1].play()
                hoptime = (780-max(feet[0][1],feet[1][1]))/15+7
                jumps += 1
                
                #fading the background

                if biome == 'boulder':
                    
                    if defaultbg != '#A0A0A0':
                        defaultbg = colourfade(defaultbg,'#A0A0A0')

                    #randomly falling boulders
                    if random.randint(0,10-effects['slipchance']) == 0:
                        ontop = [j for sublist in collisions for j, value in enumerate(sublist) if value]
                        if len(ontop) != 0:
                            randobstacle = random.choice(ontop)
                        
                            if obstacles[randobstacle]['biome'] == 'boulder' and obstacles[randobstacle]['timer'] == 0:
                                obstacles[randobstacle]['timer'] = 180

                elif biome == 'snowy':
                    if defaultbg != '#FFFFFF':
                        defaultbg = colourfade(defaultbg,'#FFFFFF')

                elif biome == 'log':
                    if defaultbg != "#A8CA59":
                        defaultbg = colourfade(defaultbg,"#A8CA59") 

                #distance of first foot and second foot
                first = (feet[0][0]-pos[0])**2 + (feet[0][1]-pos[1])**2 
                second = (feet[1][0]-pos[0])**2 + (feet[1][1]-pos[1])**2 
    
                #moving the feet to the cursor
                if first <= walkradius[0]**2+5 and not second <= walkradius[0]**2+5: feet[0] = list(pos)
                elif second <= walkradius[1]**2+5 and not first <= walkradius[1]**2+5: feet[1] = list(pos)

                #if the feet circles are overlapping 
                #and you click in the overlap it moves the closest foot
                
                elif feet[0][1] > feet[1][1]: feet[0] = list(pos)
                else: feet[1] = list(pos)

                feetdistance = math.sqrt((feet[1][0]-feet[0][0])**2 + (feet[1][1]-feet[0][1])**2)

                #if feet are too far apart or left foot isnt on the left
                if feet[0][0] > feet[1][0] or 325 < feetdistance: 
                    twisted = True
                    if scale == 0:
                        scale = 100
                    sounds[2].play()
                    
                else:
                    twisted = False
                locked = 3

    #choosing items before the game starts
    if menu == True:
        
        ignore = True
        screen.fill("#001600")
        
        screen.blit(backpack,(30,100))
        showtext("PICK ONE TO ADD",35,(width/2+50, height/2-250), "white")
        showtext("TO YOUR BACKPACK",35,(width/2+70, height/2-220), "white")

        for slot in inventory:
            #adding perks
            perk = invitems[inventory.index(slot)]

            if slot.collidepoint(pos):
               #selected:

               #colouring in the perk that is being hover over
               pygame.draw.rect(screen, "#007A59", slot)
               pygame.draw.rect(screen, "#003F37", (slot[0]+4,slot[1]+4,slot[2]-8,slot[3]-60))

               #printing the description of the perks
               if type(stats[perk]) != list:
                   showtext(stats[perk],15,(slot[0]+65,slot[1]+30), "white")

               else:
                   for x, line in enumerate(stats[perk]):
                       showtext(line,15,(slot[0]+65,slot[1]+30+15*x), "white")
                   
               if clicked == True:
                    menu = False
                    print(perk)
                    #shoes:
                    if perk == 'Left Foot':
                        walkradius[0] += 5
                        normal[0] = pygame.transform.flip(pygame.image.load('images/boot.png'), True, False)

                    elif perk == 'Right Foot':
                        walkradius[1] += 8
                        normal[1] = pygame.image.load('images/croc.png')
                        effects['slipchance'] += 3

                    elif perk == 'Water':
                        effects['stamina'] -= 0.02

                    elif perk == 'Clothes':
                        effects['heat'] -= 0.02

                    elif perk == 'Matress':
                        pass

                    else:
                        #Sleeping bag
                        pass

                    shadows[normal[0]] = shadow(normal[0],(22,22,22))
                    shadows[normal[1]] = shadow(normal[1],(22,22,22))
            else:   
                #big rect 
                pygame.draw.rect(screen, "#004433", slot)
            
                pygame.draw.rect(screen, "#002816", (slot[0]+4,slot[1]+4,slot[2]-8,slot[3]-60))

            #small rect
            pygame.draw.rect(screen, "#002816", (slot[0]+4,slot[1]+127,slot[2]-8,slot[3]-130))
            
            showtext(str(perk).upper(),23,(slot[0]+65,slot[1]+150), "white")
        clicked = False
        #screen.blit(perks,(20, height/2-140))
        
        
    else:
        bg = defaultbg
        #switching biomes
        if score/50 > biomeswitch:
            if biome == 'boulder':  biomesnowy()
            else: biomeboulder()
            biomeswitch += random.randint(40,60)
            

        #Moving the obstacles when we move:
        if hoptime > 0:
            hoptime -= hoptime/3
            if hoptime < 0.1:hoptime = 0

            for obstacle in obstacles:
                obstacle['hitbox'].y+=hoptime

            for decor in decoration:
                decor['hitbox'].y+=hoptime

            for foot in feet:
                foot[1] += hoptime

            if biome == 'snowy':
                for footprint in footprints:
                    footprint[1][1]+=hoptime

            score+=hoptime

        #fill the screen with a color to wipe away anything from last frame
        screen.fill(bg)
        
        if biome == 'snowy':
            for footprint in footprints:
                screen.blit(footprint[0],footprint[1])
                
        for decor in decoration:
            screen.blit(decor['img'],(decor['hitbox'].x,decor['hitbox'].y))
            #removing decorations if they hit the bottom and it isn't their biome
            if decor['hitbox'].y > 800:
                decor['hitbox'].y = -20
                if biome != decor['biome']:
                    decoration.remove(decor)
        
        collisions = [[],[]]
        for obstacle in obstacles[:]:
            hitbox = obstacle['hitbox']
            if obstacle['biome'] == 'log':

                if obstacle["img"] == log2:
                    #checking/printing the ladder steps 
                    screen.blit(shadows[obstacle['img']],(hitbox.x,hitbox.y+6))
                    screen.blit(log2,(hitbox.x,hitbox.y))

                elif obstacle["img"] == log1:
                    #checking/printing the tall logs
                    screen.blit(shadows[obstacle['img']],(hitbox.x-33,hitbox.y+6))
                    screen.blit(log1,(hitbox.x-33,hitbox.y))

                collisions[0].append(rect_circle_intersect(hitbox, feet[0], walkradius[0]*0.8))
                collisions[1].append(rect_circle_intersect(hitbox, feet[1], walkradius[1]*0.8))


            else:
                #checking/printing the boulders
                if obstacle['timer'] == 0:
                    screen.blit(shadows[obstacle['img']],(hitbox.x-hitbox.r,hitbox.y+4-hitbox.r))
                    screen.blit(obstacle['img'],(hitbox.x-hitbox.r,hitbox.y-hitbox.r))
                    #pygame.draw.circle(screen,"green",[hitbox.x,hitbox.y],hitbox.r)
                    collisions[0].append(circles_intersect(feet[0], walkradius[0]*0.8,[hitbox.x,hitbox.y],hitbox.r))
                    collisions[1].append(circles_intersect(feet[1], walkradius[1]*0.8,[hitbox.x,hitbox.y],hitbox.r))

                else:
                    #printing how much time is left before boulder comes back
                    showtext(str(round(obstacle['timer']/60)),74,(hitbox.x,hitbox.y), "white")
                    obstacle['timer'] -= 1
            #reset objects when the hit the bottom

            #boulders are bigger so they reset before the other shit
            if obstacle['biome'] == 'boulder': 

                if obstacle['hitbox'].y > 1000:
                    obstacle['hitbox'].x = random.randint(100,400)
                    obstacle['hitbox'].y = -100
                    obstacle['timer'] = 0
                    if biome != 'boulder':
                        obstacles.remove(obstacle)

            elif obstacle['hitbox'].y > 800:
                if biome != 'log':
                    obstacles.remove(obstacle)

                elif obstacle["img"] == log2:
                    if random.randint(0,1) == 0: obstacle['hitbox'].x = random.randint(0,100)
                    else: obstacle['hitbox'].x = random.randint(300,400)
                    obstacle['hitbox'].y = -400

                elif obstacle["img"] == log1:
                    obstacle['hitbox'].x = random.randint(100,300)
                    obstacle['hitbox'].y = -400
                
        for foot in feet:
            screen.blit(normal[feet.index(foot)], (foot[0]-75,foot[1]-75))
            if True not in collisions[feet.index(foot)] and score != 0:
                if biome == 'snowy' and scale == 0 and len(obstacles) <= 1:
                    footprints.append([shadows[normal[1]], [feet[1][0]-75,feet[1][1]-75]])
                    footprints.append([shadows[normal[0]], [feet[0][0]-75,feet[0][1]-75]])
                    scale = 200
                    sounds[0].play()

                elif scale == 0:
                    scale = 100
                    sounds[0].play()

        if twisted: 
            #make the text fade away from the screen at some point future me
            if scale!=0:
                showtext('Twisted Ankle',90,(width/2+5,height/2+5),'black')
                showtext('Twisted Ankle',90,(width/2,height/2),'white')

        if scale != 0:
            #red screen
            if biome == 'snowy' and len(obstacles) <= 1:
                tintDamage(screen,scale/200)
            else:
                tintDamage(screen,scale/100)

            #this is for when the player isn't stepping on an obstacle

            if biome == 'snowy':
                heat -= effects['heat']
                stamina -= 0.05

            elif clicked == True:
                stamina -= 10

            else: 
                stamina -= 0.2

            #making it fade away
            scale -= 2

        elif stamina < 300:
            #regeneration
            stamina += effects['stamina']

        for i in range(2):
            pygame.draw.circle(screen,"white",feet[i],walkradius[i]+1,1)

        pygame.draw.circle(screen,"red",pos,15)
        
        #stamina bar
        pygame.draw.rect(screen, "darkblue", (width/2-152,68,304,24))
        pygame.draw.rect(screen, "blue", (width/2-150,70,stamina,20))
        screen.blit(bolt, (width/2-170,58))

        #heat bar
        pygame.draw.rect(screen, "red", (width/2-152,100,304,24))
        pygame.draw.rect(screen, "orange", (width/2-150,102,heat,20))
        screen.blit(fire, (width/2+130,90))

        #displaying score
        showtext(str(int(score/50)),74,(width/2,35), "white")

        #you die if you run out of stamina or your feet are off the screen
        if stamina <= 0 or heat <=0 or heat >= 300 or feet[0][1] > height or feet[1][1] > height: 
            print("STATS:")
            print("  Score:",round(score/50,2))
            print("  Jumps:", jumps)
            exit()
            
        clicked = False

    pygame.display.flip()
    clock.tick(60)  # limits FPS to 60

pygame.quit()