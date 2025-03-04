import pygame
import random
import os
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 540, 960
display = pygame.display.set_mode((WIDTH, HEIGHT), 0, 32)
screen = pygame.Surface((WIDTH/2, HEIGHT/2))

# Colors
white = (255, 255, 255)

# Raindrops properties
water = []
for _ in range(10):  # Number of raindrops
    x = random.randint(0, WIDTH/2)
    y = random.randint(0, HEIGHT/2)
    size = random.randint(-250, 0)

    water.append({"pos" : (x, y), "size": size})

def image_variety(images, key):
    original = images[key]
    flipped = images[f"{key}_flipped"]

    return random.choice([original, flipped])

def circles_intersect(circle1_pos, circle1_radius, circle2_pos, circle2_radius):
    # Calculate the distance between the centers of the circles
    distance = math.sqrt((circle1_pos[0] - circle2_pos[0])**2 + (circle1_pos[1] - circle2_pos[1])**2)

    # Check if the distance is less than the sum of the radii
    if distance < circle1_radius + circle2_radius:
        return True
    else:
        return False

# Main loop
running = True
clock = pygame.time.Clock()

files = os.listdir('data/images')
images = {}

for file in files:
    if '.png' in file:
        images[file.replace('.png', '')] = pygame.image.load(f'data/images/{file}')
    else:
        for item in os.listdir(f'data/images/{file}'):
            images[item.replace('.png', '')] = pygame.image.load(f'data/images/{file}/{item}')

for image in images.copy():
    images[f"{image}_flipped"] = pygame.transform.flip(images[image], True, False)

lilys = []
avoid = []

for i in range(10):
    rnum = random.randint(1, 3)
    size = [25, 19, 13][rnum - 1]

    img = image_variety(images, f"lily_{rnum}")
    x = random.randint(0, WIDTH/2 - size*2)
    y = 45*i

    if not any(circles_intersect([item[0][0] + item[1], item[0][1] + item[1]], item[1], [x + size, y + size], size + 5) for item in avoid):
        avoid.append([[x, y], size])
        lilys.append([img, (x, y)])
    else:
        print("!")


while running:
    screen.fill('light blue')  # Clear screen with a black background
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update raindrops
    for drop in water:

        if drop["size"] > 51:
            drop["size"] = -20
            drop["pos"] = (random.randint(0, WIDTH/2), random.randint(0, HEIGHT/2))

        drop["size"] += 1
        if drop["size"] > 0:
            # Draw the raindrop with semi-transparency
            circle_surface = pygame.Surface((drop["size"] * 2, drop["size"] * 2), pygame.SRCALPHA)
            circle_surface.set_alpha(255 - drop["size"]*5)  # Set transparency level (0 is fully transparent, 255 is fully opaque)

            # Draw the circle on the surface
            pygame.draw.circle(circle_surface, 'white', (drop["size"], drop["size"]), drop["size"], 1)
            if drop["size"] > 20:
                pygame.draw.circle(circle_surface, 'white', (drop["size"], drop["size"]), drop["size"] - 6, 1)
            if drop["size"] > 40:
                pygame.draw.circle(circle_surface, 'white', (drop["size"], drop["size"]), drop["size"] - 15, 1)
            
            screen.blit(circle_surface, (drop["pos"][0] - drop["size"], drop["pos"][1] - drop["size"]))

    for lily in lilys:
        screen.blit(lily[0], lily[1])

    # Update the display
    display.blit(pygame.transform.scale(screen, display.get_size()), (0, 0))
    pygame.display.flip()
    clock.tick(60)
    clicking = False

# Quit Pygame
pygame.quit()