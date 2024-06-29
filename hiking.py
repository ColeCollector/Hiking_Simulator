import pygame, random, math
height = 800
width = 450


# pygame setup
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

invitems = {"Water" : ["plastic bottle","metal bottle", "water jug"],"Matress":["no matress","inflatable matress","foam cushioned matress"],"Sleeping Bag":["light bag(10C)","3 season bag(-5C)","winter bag(-40)"], "Left Foot":["crocs","hiking boots","work boots"],"Right Foot":["crocs","hiking boots","work boots"], "Clothes":["no spare clothes","an extra of everything","7 days of clothes"]}
invitems = list(invitems.keys())

log1 = pygame.image.load('images/log_1.png')
log2 = pygame.image.load('images/log_2.png')

boulder = pygame.image.load('images/boulder.png')
boulder2 = pygame.image.load('images/boulder2.png')
fboulder = pygame.transform.flip(boulder, True, False)

# Obstacles properties
obstacle_width = 100
obstacle_height = 20
obstacles = []

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


def shadow(image):
    image = image.convert_alpha()
    imgwidth, imgheight = image.get_size()
    image.lock()

    # Iterate over each pixel
    for x in range(imgwidth):
        for y in range(imgheight):
            color = image.get_at((x, y))
            if color.a != 0:
                image.set_at((x, y), (40, 40, 40, color.a))

    # Unlock the surface
    image.unlock()
    return image

shadows = {
    log1 : shadow(log1),
    log2 : shadow(log2),
    boulder : shadow(boulder),
    fboulder : shadow(fboulder),
    boulder2 : shadow(boulder2)
    }


normal = [pygame.transform.flip(pygame.image.load('images/foot.png'), True, False),pygame.image.load('images/foot.png')]
#bloody = [pygame.transform.flip(pygame.image.load('images/bloody.png'), True, False),pygame.image.load('images/bloody.png')]

health = 300
hoptime = 0
score = 0
locked = 3
walkradius = [80,80]


jumps = 0
slipchance = 0
inventory = []
#footprints = []

for collumn in range(2):
    for row in range(3): inventory.append(pygame.Rect((20+(140*row), height/2-150+(200*collumn),130,180)))
#for row in range(2): inventory.append(pygame.Rect((170+(90*row), height/2-50,80,80)))

#inventory.append(pygame.Rect((100+(110), height/2+60,100,100)))

running = True
clicked = False
menu = True
ignore = False
biome = "log"
boulderstart = 3

defaultbg = "#442323"
bg = defaultbg
feet = [[width/2-100,700],[width/2+100,700]]

#backround audio
pygame.mixer.music.load('sounds/ambience.wav')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.05)


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
    intermediate_rgb = tuple(int(start + (end - start) * 0.07) for start, end in zip(start_rgb, end_rgb))
    
    # Check if intermediate color is close enough to end color
    if all(abs(c1 - c2) <= 30 for c1, c2 in zip(intermediate_rgb, end_rgb)):
        return hex_end
    
    # Convert intermediate RGB back to hex
    intermediate_hex = '#{:02x}{:02x}{:02x}'.format(*intermediate_rgb)
    
    return intermediate_hex


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

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            ignore = True
            locked = 3

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            ignore = False

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 :
            clicked = True
            #this if statement is here because theres a weird glitch with the
            #starting inventory menu if its not there
            if ignore == False:
                hoptime = 15
                jumps += 1
                
                if biome == 'boulder':
                    #fading the background
                    if defaultbg != '#69B1EF':
                        if score/50 > boulderstart+5:
                            defaultbg = colourfade(defaultbg,'#69B1EF')

                    #randomly falling boulders
                    if random.randint(0,7-slipchance) == 0:
                        randobstacle = random.randint(0,len(obstacles)-1)
                        
                        if obstacles[randobstacle]['biome'] == 'boulder' and obstacles[randobstacle]['timer'] == 0:
                            obstacles[randobstacle]['timer'] = 180

                #distance of first foot and second foot
                first = (feet[0][0]-pos[0])**2 + (feet[0][1]-pos[1])**2 
                second = (feet[1][0]-pos[0])**2 + (feet[1][1]-pos[1])**2 

                #moving the feet to the cursor
                if first <= walkradius[0]**2+5 and not second <= walkradius[0]**2+5: feet[0] = list(pos)
                elif second <= walkradius[0]**2+5 and not first <= walkradius[0]**2+5: feet[1] = list(pos)

                #if the feet circles are overlapping 
                #and you click in the overlap it moves the closest foot
                
                elif feet[0][1] > feet[1][1]: feet[0] = list(pos)
                else: feet[1] = list(pos)

                feetdistance = math.sqrt((feet[1][0]-feet[0][0])**2 + (feet[1][1]-feet[0][1])**2)

                #if feet are too far apart or left foot isnt on the left
                if feet[0][0] > feet[1][0] or 325 < feetdistance: bg = "red"
                else: bg = defaultbg
                locked = 3

    #choosing items before the game starts
    if menu == True:
        ignore = True
        screen.fill("black")
        showtext("PICK ONE",74,(width/2, height/2-190), "white")

        for slot in inventory:
            #adding perks
            perk = invitems[inventory.index(slot)]

            if slot.collidepoint(pos):
               pygame.draw.rect(screen, "gray", slot)
               if clicked == True:
                    menu = False
                    print(perk)
                    #shoes:
                    if perk == 'Left Foot':
                        walkradius[0] += 10
                        normal = [pygame.transform.flip(pygame.image.load('images/boot.png'), True, False),pygame.image.load('images/foot.png')]

                    elif perk == 'Right Foot':
                        walkradius[1] += 15
                        normal = [pygame.transform.flip(pygame.image.load('images/foot.png'), True, False),pygame.image.load('images/croc.png')]
                        slipchance += 3
            else:   
                pygame.draw.rect(screen, "white", slot)
            
            pygame.draw.rect(screen, "gray", (slot[0]+3,slot[1]+127,slot[2]-6,slot[3]-130))
            showtext(str(perk),30,(slot[0]+65,slot[1]+150), "black")

    else:
        #switching biomes
        if biome != 'boulder' and score/50 > boulderstart:
            biome = 'boulder'
            #generating new obstacles
            for i in range(5):
                obstacle_x = random.randint(100,400)
                obstacle_y = i*200 - 1400
                randomchoice = random.randint(0,2)

                obstacles.append({
                    "hitbox" : Hitbox(obstacle_x, obstacle_y,[112,112,90][randomchoice]),
                    "img" : [boulder,fboulder,boulder2][randomchoice],
                    "biome" : "boulder",
                    "timer" : 0
                    })


        #Moving the obstacles when we move:
        if hoptime > 0:
            hoptime -= hoptime/3
            if hoptime < 0.1:hoptime = 0

            for obstacle in obstacles:
                obstacle['hitbox'].y+=hoptime

            for foot in feet:
                foot[1] += hoptime

            #for footprint in footprints:
            #    footprint[1][1]+=hoptime
            score+=hoptime

        #fill the screen with a color to wipe away anything from last frame
        screen.fill(bg)

        #for footprint in footprints:
        #    screen.blit(footprint[0],footprint[1])

        collisions = [[],[]]
        for obstacle in obstacles[:]:
            hitbox = obstacle['hitbox']
            if type(hitbox) == pygame.Rect:

                if obstacle["img"] == log2:

                    #checking/printing the ladder steps 
                    screen.blit(shadows[obstacle['img']],(hitbox.x,hitbox.y+4))
                    screen.blit(log2,(hitbox.x,hitbox.y))

                elif obstacle["img"] == log1:
                    #checking/printing the tall logs
                    screen.blit(shadows[obstacle['img']],(hitbox.x-33,hitbox.y+4))
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
                if biome != 'boulder':
                    obstacles.remove(obstacle)

                if obstacle['hitbox'].y > 1000:
                    obstacle['hitbox'].x = random.randint(100,400)
                    obstacle['hitbox'].y = -100
                    obstacle['timer'] = 0


            elif obstacle['hitbox'].y > 800:
                if biome != 'log':
                    obstacles.remove(obstacle)

                else:
                    if obstacle["img"] == log2:
                        if random.randint(0,1) == 0: obstacle['hitbox'].x = random.randint(0,100)
                        else: obstacle['hitbox'].x = random.randint(300,400)
                        obstacle['hitbox'].y = -400

                    if obstacle["img"] == log1:
                        obstacle['hitbox'].x = random.randint(100,300)
                        obstacle['hitbox'].y = -400
                
        for foot in feet:
            screen.blit(normal[feet.index(foot)], (foot[0]-75,foot[1]-75))
            if True not in collisions[feet.index(foot)]:
                if clicked == True:
                    #footprints.append([bloody[feet.index(foot)], [foot[0]-75,foot[1]-75]])
                    health -= 10
                else:
                    health -= 0.2

        if bg == "red":
            health -= 0.3

        #regeneration
        elif health < 300:
            health += 0.1
            
        for i in range(2):
            pygame.draw.circle(screen,"white",feet[i],walkradius[i]+1,1)

        pygame.draw.circle(screen,"red",pos,15)
        
        #stamina bar
        pygame.draw.rect(screen, "darkblue", (width/2-152,68,304,24))
        pygame.draw.rect(screen, "blue", (width/2-150,70,health,20))

        #displaying score
        showtext(str(int(score/50)),74,(width/2,35), "white")

        #you die if you run out of health or your feet are off the screen
        if health <= 0 or (feet[0][1] > height or feet[1][1] > height): 
            print("STATS:")
            print("  Score:",round(score/50,2))
            print("  Jumps:", jumps)
            exit()
            
        clicked = False

    pygame.display.flip()
    clock.tick(60)  # limits FPS to 60

pygame.quit()