import pygame,random
height = 800
width = 500

# Obstacles properties
obstacle_width = 115
obstacle_height = 20
obstacles = []

for i in range(7):
    if random.randint(0,1) == 0: obstacle_x = random.randint(0,100)
    else: obstacle_x = random.randint(350,450)
        
    obstacle_y = i*100
    obstacles.append(pygame.Rect(obstacle_x, obstacle_y, obstacle_width, obstacle_height))

obstacle_height = 500
obstacle_width = 100

obstacle_x = random.randint(200,300)
obstacle_y = random.randint(0, 500)
obstacles.append(pygame.Rect(obstacle_x, obstacle_y, obstacle_width, obstacle_height))

# pygame setup
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
running = True
walkradius = 100
down_pos = [width/2,700]
hoptime = 0
image = pygame.image.load('foot.png')

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:


            if (down_pos[0]-pos[0])**2 + (down_pos[1]-pos[1])**2 < walkradius**2:
                down_pos = pos
                for obstacle in obstacles:
                    hoptime = 30
            else:

                pass
    
    #Moving the obstacles when we move:
    if hoptime > 0:
        hoptime -= hoptime/3
        if hoptime < 0.1:hoptime = 0

        for obstacle in obstacles:
            obstacle.y+=hoptime
    
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("#87ceeb")
    pygame.draw.circle(screen,"white",down_pos,walkradius+1)
    pygame.draw.circle(screen,"#87ceeb",down_pos,walkradius)
    pygame.draw.circle(screen,"red",pos,20)
    

    # RENDER YOUR GAME HERE
    for obstacle in obstacles:
        pygame.draw.rect(screen, "#879ceb", obstacle)

        if obstacle.y > 800:
            obstacle.y = 0
            if obstacle.height < 500:
                if random.randint(0,1) == 0: obstacle.x = random.randint(0,100)
                else: obstacle.x = random.randint(400,500)
            #else:
            #    pass
    
    #pygame.draw.circle(screen,"black",down_pos,20)
    screen.blit(image, (down_pos[0]-75,down_pos[1]-75))

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()