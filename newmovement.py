import pygame,math

height = 800
width = 500

# pygame setup
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
running = True
walkradius = [85,80]
feet = [[width/2-100,700],[width/2+100,700]]
ignore = False
locked = 3

def closest_point_on_circle(pos, locked):
    distance = math.sqrt((pos[0] - feet[locked][0])**2 + (pos[1] - feet[locked][1])**2)
    closest_x = feet[locked][0] + walkradius[locked] * (pos[0] - feet[locked][0]) / distance
    closest_y = feet[locked][1] + walkradius[locked] * (pos[1] - feet[locked][1]) / distance

    return [closest_x, closest_y]
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    pos = pygame.mouse.get_pos()

    mouse_buttons = pygame.mouse.get_pressed()
    if mouse_buttons[0] and ignore == False:
        if locked != 3:
            pos = closest_point_on_circle(pos,locked)
        else:
            distances = [None, None]
            for i in range(2):
                if not (feet[i][0]-pos[0])**2 + (feet[i][1]-pos[1])**2 < walkradius[i]**2 + 5:
                    distances[i] = (math.sqrt((pos[0] - feet[i][0])**2 + (pos[1] - feet[i][1])**2))

            #if the mouse is not in one of the circles
            if None not in distances:
                if distances[0] > distances[1]: 
                    pos = closest_point_on_circle(pos,1)
                    locked = 1

                else: 
                    pos = closest_point_on_circle(pos,0)
                    locked = 0
        

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            # Moving the feet to the cursor

            if locked == 0:
                feet[0] = list(pos)

            elif locked == 1:
                feet[1] = list(pos)

            elif distances[0] == None and distances[1] != None: 
                feet[0] = list(pos)


            elif distances[1] == None and distances[0] != None: 
                feet[1] = list(pos)

            # If the feet circles are overlapping 
            # And you click in the overlap it moves the closest foot
            
            elif feet[0][1] > feet[1][1]: 
                feet[0] = list(pos)
            else: 
                feet[1] = list(pos)

            locked = 3

    screen.fill("#69B1EF")

    for foot in feet:
        pygame.draw.circle(screen,"white",foot,walkradius[feet.index(foot)]+1,1)
        pygame.draw.circle(screen,"black",foot,20)
        
    pygame.draw.circle(screen,"red",pos,20)
    pygame.display.flip()
    clock.tick(60)

pygame.quit()