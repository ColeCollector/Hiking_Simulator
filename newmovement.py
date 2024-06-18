import pygame,random,math,numpy as np

height = 800
width = 500


# pygame setup
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
running = True
walkradius = 80
feet = [[width/2-100,700],[width/2+100,700]]
ignore = False
locked = 3

def closest_point_on_circle(pos, foot, walkradius):
    distance = math.sqrt((pos[0] - foot[0])**2 + (pos[1] - foot[1])**2)
    closest_x = foot[0] + walkradius * (pos[0] - foot[0]) / distance
    closest_y = foot[1] + walkradius * (pos[1] - foot[1]) / distance

    return [closest_x, closest_y]

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
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

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            ignore = True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            ignore = False

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and ignore == False:
            locked = 3
            #updating the feet positions
            if (feet[0][0]-pos[0])**2 + (feet[0][1]-pos[1])**2 <= walkradius**2+1:
                if pos[0] < width/2-50:
                    feet[0] = pos

            elif (feet[1][0]-pos[0])**2 + (feet[1][1]-pos[1])**2 <= walkradius**2+1:
                if pos[0] > width/2+50:
                    feet[1] = pos

    screen.fill("#69B1EF")

    for foot in feet:
        pygame.draw.circle(screen,"white",foot,walkradius+1)
        pygame.draw.circle(screen,"#69B1EF",foot,walkradius)
        pygame.draw.circle(screen,"black",foot,20)
    
    pygame.draw.circle(screen,"red",pos,20)

    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()