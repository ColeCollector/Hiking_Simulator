import pygame, random, math
height = 800
width = 500

# Obstacles properties
obstacle_width = 100
obstacle_height = 20
obstacles = []

invitems = {"tent" : ["light tent","standard tent", "multi-person tent"],"matress":["no matress","inflatable matress","foam cushioned matress"],"sleeping bag":["light bag(10C)","3 season bag(-5C)","winter bag(-40)"], "shoes1":["crocs","hiking boots","work boots"],"shoes2":["crocs","hiking boots","work boots"], "clothes":["no spare clothes","an extra of everything","7 days of clothes"]}
invitems = ["light tent","standard tent", "multi-person tent"],["no matress","inflatable matress","foam cushioned matress"],["light bag(10C)","3 season bag(-5C)","winter bag(-40)"],["crocs","hiking boots","work boots"],["crocs","hiking boots","work boots"],["no spare clothes","an extra of everything","7 days of clothes"]

for i in range(7):
    if random.randint(0,1) == 0: obstacle_x = random.randint(0,100)
    else: obstacle_x = random.randint(300,400)
        
    obstacle_y = i*100
    obstacles.append(pygame.Rect(obstacle_x, obstacle_y, obstacle_width, obstacle_height))

obstacle_height = 400
obstacle_width = 90

obstacle_x = random.randint(100,400)
obstacle_y = random.randint(0, 500)
obstacles.append(pygame.Rect(obstacle_x, obstacle_y, obstacle_width, obstacle_height))

cloud1 = pygame.image.load('cloud_1.png')
cloud2 = pygame.image.load('cloud_2.png')
cloud3 = pygame.image.load('cloud_3.png')
log1 = pygame.image.load('log_1.png')
log2 = pygame.image.load('log_2.png')

normal = [pygame.transform.flip(pygame.image.load('foot.png'), True, False),pygame.image.load('foot.png')]
bloody = [pygame.transform.flip(pygame.image.load('bloody.png'), True, False),pygame.image.load('bloody.png')]

clouds = []
for i in range(10):
    cloud_x = random.randint(-150,500)
    cloud_y = i*100
    clouds.append([random.choice([cloud1,cloud2,cloud3]),[cloud_x, cloud_y]])

# pygame setup
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

walkradius = 100
health = 300
hoptime = 0
score = 0
locked = 3

#setting up inventory
inventory = []

for collumn in range(2):
    for row in range(3): inventory.append(pygame.Rect((125+(90*row), height/2-80+(90*collumn),80,80)))
#for row in range(2): inventory.append(pygame.Rect((170+(90*row), height/2-50,80,80)))

#inventory.append(pygame.Rect((100+(110), height/2+60,100,100)))

footprints = []
running = True
clicked = False
menu = True
ignore = False

walkradius = 80
feet = [[width/2-100,700],[width/2+100,700]]

font = pygame.font.Font(None, 74) 
darken = pygame.Surface((width, height), pygame.SRCALPHA)       
darken.fill((0, 0, 0, 128))   

#backround audio
pygame.mixer.music.load('ambience.wav')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.05)


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

def closest_point_on_circle(pos, foot, walkradius):
    distance = math.sqrt((pos[0] - foot[0])**2 + (pos[1] - foot[1])**2)
    closest_x = foot[0] + walkradius * (pos[0] - foot[0]) / distance
    closest_y = foot[1] + walkradius * (pos[1] - foot[1]) / distance

    return [closest_x, closest_y]

while running:
    pos = pygame.mouse.get_pos()


    mouse_buttons = pygame.mouse.get_pressed()
    if mouse_buttons[0]:

        if locked != 3:
            pos = closest_point_on_circle(pos,feet[locked],walkradius)
        else:
            distances = []
            for foot in feet:
                if not (foot[0]-pos[0])**2 + (foot[1]-pos[1])**2 < walkradius**2:
                    distances.append(math.sqrt((pos[0] - foot[0])**2 + (pos[1] - foot[1])**2))

            #if the mouse is not in one of the circles
            if len(distances) == 2:
                if distances[0] > distances[1]: 
                    pos = closest_point_on_circle(pos,feet[1],walkradius)
                    locked = 1
                else: 
                    pos = closest_point_on_circle(pos,feet[0],walkradius)
                    locked = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            ignore = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            ignore = False

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and ignore == False:
            locked = 3
            #updating the feet positions
            if (feet[0][0]-pos[0])**2 + (feet[0][1]-pos[1])**2 <= walkradius**2+1:
                if pos[0] < width/2-50:
                    feet[0] = list(pos)

            elif (feet[1][0]-pos[0])**2 + (feet[1][1]-pos[1])**2 <= walkradius**2+1:
                if pos[0] > width/2+50:
                    feet[1] = list(pos)
    


    #choosing items before the game starts
    if menu == True:
        screen.fill("black")

        text = font.render("Pick one", True, "white")
        text_rect = text.get_rect(center=(width/2, height/2-150)) 
        screen.blit(text, text_rect)

        for slot in inventory:
            if slot.collidepoint(pos):
               pygame.draw.rect(screen, "gray", slot)
               if clicked == True:
                   menu = False
                   print(invitems[inventory.index(slot)])
            else:
                pygame.draw.rect(screen, "white", slot)
                    
    
    else:

        #Moving the obstacles when we move:

        for obstacle in obstacles:
            obstacle.y+=1

        for cloud in clouds:
            cloud[1][1] += 1

        for footprint in footprints:
            footprint[1][1]+=1
        
 
        for foot in feet:
            foot[1] += 1
        score+=0.1
        
        #fill the screen with a color to wipe away anything from last frame
        screen.fill("#69B1EF")
        

        
        for foot in feet:
            pygame.draw.circle(screen,"white",foot,walkradius+1)
            pygame.draw.circle(screen,"#69B1EF",foot,walkradius)


        #drawing circles and such
        #pygame.draw.circle(screen,"white",down_pos,walkradius+1)
        #pygame.draw.circle(screen,"#69B1EF",down_pos,walkradius)
        #pygame.draw.circle(screen,"gray",down_pos,walkradius*0.75)

        
        for cloud in clouds:
            screen.blit(cloud[0],cloud[1])
            cloud[1][0] += 1

            #when clouds drift off the screen
            if cloud[1][0] > width: cloud[1][0] = -150
            if cloud[1][1] > height: cloud[1][1] = -50

        

        for footprint in footprints:
            screen.blit(footprint[0],footprint[1])

        collisions = [[],[]]
        for obstacle in obstacles:
            if obstacle.height < 400:
                screen.blit(log2,(obstacle.x,obstacle.y))

            else:
                screen.blit(log1,(obstacle.x-33,obstacle.y))
                #pygame.draw.rect(screen, "white", obstacle)
            
            collisions[0].append(rect_circle_intersect(obstacle, feet[0], walkradius*0.8))
            collisions[1].append(rect_circle_intersect(obstacle, feet[1], walkradius*0.8))

            #reset objects when the hit the bottom
            if obstacle.y > 800:
                
                if obstacle.height < 400:
                    if random.randint(0,1) == 0: obstacle.x = random.randint(0,100)
                    else: obstacle.x = random.randint(300,400)
                    obstacle.y = -50
                else:
                    obstacle.x = random.randint(100,400)
                    obstacle.y = -550
        
        for foot in feet:
            screen.blit(normal[feet.index(foot)], (foot[0]-75,foot[1]-75))
            if clicked == True and True not in collisions[feet.index(foot)]:
                footprints.append([bloody[feet.index(foot)], [foot[0]-75,foot[1]-75]])
                health -= 15

        pygame.draw.circle(screen,"red",pos,15)
        
        #health bar
        pygame.draw.rect(screen, "darkgreen", (width/2-152,68,304,24))
        pygame.draw.rect(screen, "green", (width/2-150,70,health,20))

        #displaying score
        text = font.render(str(int(score/50)), True, "white")
        text_rect = text.get_rect(center=(width/2, 35)) 
        screen.blit(text, text_rect)

        if health <= 0: exit()
        
        clicked = False

        #pygame.draw.circle(screen,"black",down_pos,20)
    


    pygame.display.flip()
    clock.tick(60)  # limits FPS to 60

pygame.quit()