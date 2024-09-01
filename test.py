import pygame
import math
import random

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((500, 800))  # Set screen dimensions
clock = pygame.time.Clock()
running = True

# Initialize feet positions and walk radii
feet = [[500 / 2 - 100, 700], [500 / 2 + 100, 700]]
walkradius = [100, 80]  # Different radii for each foot
locked = -1  # No foot is locked initially

# Define the forbidden circle
forbidden_center = [250, 400]  # Example position of the forbidden circle
forbidden_radius = 100  # Radius of the forbidden circle

def closest_point_on_circle(pos, center, radius):
    """
    Calculate the closest point on the circle defined by the center and radius.
    """
    dx = pos[0] - center[0]
    dy = pos[1] - center[1]
    distance = math.sqrt(dx * dx + dy * dy)
    if distance == 0:
        return center
    ratio = radius / distance
    closest_x = center[0] + dx * ratio
    closest_y = center[1] + dy * ratio
    return [closest_x, closest_y]

def is_within_circle(pos, center, radius):
    """
    Check if the position is within the circle defined by the center and radius.
    """
    dx = pos[0] - center[0]
    dy = pos[1] - center[1]
    return dx * dx + dy * dy < radius * radius

def adjust_position_if_in_forbidden_circle(pos):
    """
    Adjust the position if it is within the forbidden circle.
    """
    if is_within_circle(pos, forbidden_center, forbidden_radius):
        pos = closest_point_on_circle(pos, forbidden_center, forbidden_radius)
    return pos

def circles_intersect(circle1_pos, circle1_radius, circle2_pos, circle2_radius):
    # Calculate the distance between the centers of the circles
    distance = math.sqrt((circle1_pos[0] - circle2_pos[0])**2 + (circle1_pos[1] - circle2_pos[1])**2)

    # Check if the distance is less than the sum of the radii
    if distance < circle1_radius + circle2_radius:
        return True
    else:
        return False

lily = [pygame.image.load('images/lily_1.png'),pygame.image.load('images/lily_2.png'), pygame.image.load('images/lily_3.png'), pygame.image.load('images/lily_4.png')]

circles = []
avoid = [[forbidden_center, forbidden_radius]]

amount = [50] * 7 + [38] * 12 + [25] * 14 + [16] * 25

for size in amount:
    attempt = 0

    while attempt < 50:
        attempt += 1
        x = random.randint(0, 500)
        y = random.randint(0, 800)

        if not any(circles_intersect([item[0][0] + item[1], item[0][1] + item[1]], item[1], [x + size, y + size], size + 5) for item in avoid):
            avoid.append([[x, y], size])
            circles.append([[x, y], size])
            break

print(len(circles))
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
    
    # Clear the screen
    screen.fill('#138099')

    # Draw the feet circles
    for i, foot in enumerate(feet):
        pygame.draw.circle(screen, pygame.Color("white"), foot, walkradius[i] + 1, 1)
        pygame.draw.circle(screen, pygame.Color("black"), foot, 20)
    
    # Draw the forbidden circle
    pygame.draw.circle(screen, pygame.Color("red"), forbidden_center, forbidden_radius, 2)

    for circle in circles:
        if circle[1] == 38:
            screen.blit(lily[0],circle[0])

        elif circle[1] == 25:
            screen.blit(lily[1],circle[0])

        elif circle[1] == 50:
            screen.blit(lily[2],circle[0])

        elif circle[1] == 16:
            screen.blit(lily[3],circle[0])

    # Draw the position circle
    pygame.draw.circle(screen, pygame.Color("red"), pos, 20)
    pygame.display.flip()
    clock.tick(60)  # Limit the frame rate to 60 FPS

pygame.quit()
