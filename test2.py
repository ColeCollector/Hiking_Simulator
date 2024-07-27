import pygame, math
from boulder import Boulders




# Initialize Pygame
pygame.init()

WIDTH, HEIGHT = 450, 800
# Set up display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Example")

# Main game loop



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

boulders = Boulders(images)

feet = [[WIDTH/2-100,700],[WIDTH/2+100,700]]

walkradius = [80, 80]  # Different radii for each foot
locked = -1  # No foot is locked initially

# Define the forbidden circle
forbidden_center = [250, 400]  # Example position of the forbidden circle
forbidden_radius = 100  # Radius of the forbidden circle
speed = 0 
stamina = 300
heat = 150


def closest_point_on_circle(pos, center, radius):
    dx = pos[0] - center[0]
    dy = pos[1] - center[1]
    distance = math.sqrt(dx * dx + dy * dy)
    ratio = radius / distance
    closest_x = center[0] + dx * ratio
    closest_y = center[1] + dy * ratio
    return [closest_x, closest_y]

def is_within_circle(pos, center, radius):
    dx = pos[0] - center[0]
    dy = pos[1] - center[1]
    return dx * dx + dy * dy < radius * radius

def adjust_position_if_in_forbidden_circle(pos):

    if is_within_circle(pos, forbidden_center, forbidden_radius):
        pos = closest_point_on_circle(pos, forbidden_center, forbidden_radius)
    return pos

running = True

while running:
    pos = pygame.mouse.get_pos()  # Get current mouse position
    mouse_buttons = pygame.mouse.get_pressed()  # Get mouse button states
    
    if mouse_buttons[0]:  # If left mouse button is pressed
        
        if locked != -1:  # If a foot is locked
            pos = closest_point_on_circle(pos, feet[locked], walkradius[locked])
            pos = adjust_position_if_in_forbidden_circle(pos)
        else:  # If no foot is locked
            distances = [math.hypot(pos[0] - foot[0], pos[1] - foot[1]) for foot in feet]
            if all(dist > walkradius[i] for i, dist in enumerate(distances)):
                locked = distances.index(min(distances))
                pos = closest_point_on_circle(pos, feet[locked], walkradius[locked])
                pos = adjust_position_if_in_forbidden_circle(pos)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # If the user closes the window
            running = False

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # If the left mouse button is released
            speed = (780-max(feet[0][1],feet[1][1]))/15+7
            if locked != -1:  # If a foot is locked
                pos = adjust_position_if_in_forbidden_circle(pos)
                feet[locked] = list(pos)
            else:
                # Check if the position is within any foot's radius
                if any(math.hypot(pos[0] - foot[0], pos[1] - foot[1]) <= walkradius[i] for i, foot in enumerate(feet)):
                    for i, foot in enumerate(feet):
                        if math.hypot(pos[0] - foot[0], pos[1] - foot[1]) <= walkradius[i]:
                            pos = adjust_position_if_in_forbidden_circle(pos)
                            feet[i] = list(pos)
                            break
                else:  # Move the closest foot if the position is outside all radii
                    pos = adjust_position_if_in_forbidden_circle(pos)
                    feet[distances.index(min(distances))] = list(pos)
            locked = -1  # Unlock the foot
    
    
    # Fill the screen with a color
    screen.fill((0, 0, 0))

    speed -= speed/3
    if speed < 0.1:speed = 0

    for i, foot in enumerate(feet):
        foot[1] += speed
        screen.blit(normal[i], (foot[0]-75,foot[1]-75))
        pygame.draw.circle(screen, pygame.Color("white"), foot, walkradius[i] + 1, 1)

    # Draw the forbidden circle
    pygame.draw.circle(screen, pygame.Color("red"), forbidden_center, forbidden_radius, 2)
    
    # Draw the position circle
    pygame.draw.circle(screen, pygame.Color("red"), pos, 20)
    
    
    collisions = [[],[]]

    boulders.update(speed)
    boulders.render(screen)  

    #stamina bar
    pygame.draw.rect(screen, "darkblue", (WIDTH/2-152,68,304,24))
    pygame.draw.rect(screen, "blue", (WIDTH/2-150,70,stamina,20))
    screen.blit(images['bolt'], (WIDTH/2-170,58))

    #heat bar
    pygame.draw.rect(screen, "red", (WIDTH/2-152,100,304,24))
    pygame.draw.rect(screen, "orange", (WIDTH/2-150,102,heat,20))
    screen.blit(images['fire'], (WIDTH/2+130,90))

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()

