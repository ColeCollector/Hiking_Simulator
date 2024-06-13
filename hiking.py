import pygame, random, math
height = 800
width = 500

# Obstacles properties
obstacle_width = 100
obstacle_height = 20
obstacles = []

for i in range(7):
    if random.randint(0,1) == 0: obstacle_x = random.randint(0,100)
    else: obstacle_x = random.randint(300,400)
        
    obstacle_y = i*100
    obstacles.append(pygame.Rect(obstacle_x, obstacle_y, obstacle_width, obstacle_height))

obstacle_height = 400
obstacle_width = 90

obstacle_x = random.randint(200,300)
obstacle_y = random.randint(0, 500)
obstacles.append(pygame.Rect(obstacle_x, obstacle_y, obstacle_width, obstacle_height))

cloud1 = pygame.image.load('cloud_1.png')
cloud2 = pygame.image.load('cloud_2.png')
cloud3 = pygame.image.load('cloud_3.png')
log1 = pygame.image.load('log_1.png')
log2 = pygame.image.load('log_2.png')
foot = pygame.image.load('foot.png')
bloody = pygame.image.load('bloody.png')

clouds = []
for i in range(7):
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

footprints = []
running = True
clicked = False
menu = False

down_pos = [width/2,700]

font = pygame.font.Font(None, 74) 
darken = pygame.Surface((width, height), pygame.SRCALPHA)       
darken.fill((0, 0, 0, 128))   

#backround audio
pygame.mixer.music.load('ambience.wav')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.05)

def point_inside_circle(point, circle_center, circle_radius):
    return math.hypot(point[0] - circle_center[0], point[1] - circle_center[1]) <= circle_radius

def rect_circle_intersect(rect, circle_center, circle_radius):
    #Check if any corner of the rectangle is inside the circle
    corners = [
        rect.topleft,
        rect.topright,
        rect.bottomleft,
        rect.bottomright
    ]
    for corner in corners:
        if point_inside_circle(corner, circle_center, circle_radius):
            return True

    #Check if any edge of the circle intersects with any edge of the rectangle
    closest_x = max(rect.left, min(circle_center[0], rect.right))
    closest_y = max(rect.top, min(circle_center[1], rect.bottom))
    distance_x = circle_center[0] - closest_x
    distance_y = circle_center[1] - closest_y
    return distance_x ** 2 + distance_y ** 2 <= circle_radius ** 2

while running:
    pos = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
            if (down_pos[0]-pos[0])**2 + (down_pos[1]-pos[1])**2 < walkradius**2:
                down_pos = pos
                for obstacle in obstacles:
                    hoptime = 40

    #keys = pygame.key.get_pressed()

    #choosing items before the game starts
    if menu == False:
        screen.fill("black")
        for collumn in range(3):
            for row in range(5):
                pygame.draw.rect(screen, "#5B5B5B", (100+(60*row), height/2+25-(60*collumn),50,50))

        for row in range(5):
            pygame.draw.rect(screen, "white", (100+(60*row), height/2+25-(60*-1.5),50,50))

        #displaying score
        text = font.render("inventory", True, "white")
        text_rect = text.get_rect(center=(width/2, height/2-150)) 
        screen.blit(text, text_rect)


    #    if menu == False:
    #        screen.blit(darken, (0, 0))
    #        pygame.draw.rect(screen, "white", (width/2-152,height/2,304,10))
    #
    #        menu = True
            
    else:
    #    menu = False
    #Moving the obstacles when we move:
        if hoptime > 0:
            hoptime -= hoptime/3
            if hoptime < 0.1:hoptime = 0

            for obstacle in obstacles:
                obstacle.y+=hoptime
            for cloud in clouds:
                cloud[1][1] += hoptime
            for footprint in footprints:
                footprint[1][1]+=hoptime
            score+=hoptime
        
        #fill the screen with a color to wipe away anything from last frame
        screen.fill("#69B1EF")
        


        #drawing circles and such
        pygame.draw.circle(screen,"white",down_pos,walkradius+1)
        pygame.draw.circle(screen,"#69B1EF",down_pos,walkradius)
        #pygame.draw.circle(screen,"gray",down_pos,walkradius*0.75)
        
        
        for cloud in clouds:
            screen.blit(cloud[0],cloud[1])
            cloud[1][0] += 1

            #when clouds drift off the screen
            if cloud[1][0] > width:
                cloud[1][0] = -150
            if cloud[1][1] > height:
                cloud[1][1] = -50

        pygame.draw.circle(screen,"red",pos,20)

        for footprint in footprints:
            screen.blit(footprint[0],footprint[1])

        collisions = []
        for obstacle in obstacles:
            if obstacle.height < 400:
                screen.blit(log2,(obstacle.x,obstacle.y))

            else:
                screen.blit(log1,(obstacle.x-33,obstacle.y))
                #pygame.draw.rect(screen, "white", obstacle)
                
            collisions.append(rect_circle_intersect(obstacle, down_pos, walkradius*0.8))

            #reset objects when the hit the bottom
            if obstacle.y > 800:
                
                if obstacle.height < 400:
                    if random.randint(0,1) == 0: obstacle.x = random.randint(0,100)
                    else: obstacle.x = random.randint(300,400)
                    obstacle.y = -50
                else:
                    obstacle.x = random.randint(200,300)
                    obstacle.y = -550
        
        #when they are not standing on a platform
        if True not in collisions:
            screen.blit(foot, (down_pos[0]-75,down_pos[1]-75))
            health -= 0.5
            if clicked == True:
                footprints.append([bloody, [down_pos[0]-75,down_pos[1]-75]])
                health -= 15

        #when standing on a playform
        else:
            screen.blit(foot, (down_pos[0]-75,down_pos[1]-75))

        clicked = False

        #health bar
        pygame.draw.rect(screen, "darkgreen", (width/2-152,68,304,24))
        pygame.draw.rect(screen, "green", (width/2-150,70,health,20))

        #displaying score
        text = font.render(str(int(score/50)), True, "white")
        text_rect = text.get_rect(center=(width/2, 35)) 
        screen.blit(text, text_rect)

        if health <= 0:
            exit()
        

        #pygame.draw.circle(screen,"black",down_pos,20)
    


    pygame.display.flip()
    clock.tick(60)  # limits FPS to 60

pygame.quit()