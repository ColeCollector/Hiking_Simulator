from game import SCREEN_HEIGHT
import pygame,random
height = 800
width = 500

obstacle_width = 100
obstacle_height = 20
obstacles = []

for i in range(7):
    if random.randint(0,1) == 0: obstacle_x = random.randint(0,100)
    else: obstacle_x = random.randint(350,450)
        
    obstacle_y = i*100
    obstacles.append(pygame.Rect(obstacle_x, obstacle_y, obstacle_width, obstacle_height))



# pygame setup
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
running = True
walkradius = 100
down_pos = [width/2,700]

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
            else:pass

    
    print(pos)
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")
    pygame.draw.circle(screen,"white",down_pos,walkradius+1)
    pygame.draw.circle(screen,"purple",down_pos,walkradius)
    pygame.draw.circle(screen,"red",pos,20)

    pygame.draw.circle(screen,"black",down_pos,20)
    

    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()