import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600

# Create the screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Move PNG Example')

# Load the image
image = pygame.image.load('images/boot.png')  # Replace with your image file
shaddow = pygame.image.load('images/shaddow.png')
image_rect = image.get_rect()
image_rect.topleft = (100, 100)  # Starting position



# Speed of the movement
speed = 2

# Clock to control the frame rate
clock = pygame.time.Clock()

# Main loop
running = True
pos = (800,600)


while running:
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = pygame.mouse.get_pos()
            print("JUMP")



    # Calculate the distance to the target
    distance_x = pos[0] - image_rect.x
    distance_y = pos[1] - image_rect.y
    distance = math.sqrt(distance_x**2 + distance_y**2)
    speed = distance/40
    if speed < 5:
        speed = 5

    if distance != 0:
        # Calculate the direction vector and normalize it
        direction_x = distance_x / distance
        direction_y = distance_y / distance

        # Calculate the movement amount
        move_x = direction_x * speed
        move_y = direction_y * speed

        # Move the image
        image_rect.x += move_x
        image_rect.y += move_y

        # Ensure the image doesn't overshoot the target
        if abs(pos[0] - image_rect.x) < speed:
            image_rect.x = pos[0]
        if abs(pos[1] - image_rect.y) < speed:
            image_rect.y = pos[1]

    # Fill the screen with white
    screen.fill((255, 255, 255))

    # Draw the image
    print(distance)
    if distance > 100 and distance < 400:
        
        #screen.blit(shaddow, (image_rect[0]-80,image_rect[1]-80,image_rect[2],image_rect[3]))
        pygame.draw.circle(screen,"black",(image_rect[0],image_rect[1]),distance/40)
                           
    else:
        screen.blit(image, (image_rect[0]-75,image_rect[1]-75,image_rect[2],image_rect[3]))

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)



# Quit Pygame
pygame.quit()
sys.exit()
