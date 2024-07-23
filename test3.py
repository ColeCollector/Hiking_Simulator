import pygame
import random
import math

# Constants
HEIGHT = 800
WIDTH = 450

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Inventory items
inventory_items = {
    "Water": ["plastic bottle", "metal bottle", "water jug"],
    "Sleeping Bag": ["light bag(10C)", "3 season bag(-5C)", "winter bag(-40)"],
    "Left Foot": ["crocs", "hiking boots", "work boots"],
    "Right Foot": ["crocs", "hiking boots", "work boots"],
    "Locked_1": None,
    "Locked_2": None,
    "Clothes": ["no spare clothes", "an extra of everything", "7 days of clothes"]
}
inventory_keys = list(inventory_items.keys())

# Load images
image_files = {
    'log1': 'images/new/log_1.png',
    'log2': 'images/new/log_2.png',
    'rock': 'images/rock.png',
    'rock1': 'images/rock_1.png',
    'rock2': 'images/rock_2.png',
    'stick': 'images/stick.png',
    'grass': 'images/grass.png',
    'fire': 'images/fire.png',
    'bolt': 'images/bolt.png',
    'boulder': 'images/boulder.png',
    'boulder2': 'images/boulder_2.png',
    'transition1': 'images/transition_1.png',
    'transition2': 'images/transition_2.png',
    'transition3': 'images/transition_3.png',
    'backpack': 'images/backpack.png',
    'perks': 'images/new/perks.png',
    'foot': 'images/new/foot.png',
    'boot': 'images/boot.png',
    'croc': 'images/croc.png'
}

images = {key: pygame.image.load(path) for key, path in image_files.items()}
images['fstick'] = pygame.transform.flip(images['stick'], True, False)
images['fboulder'] = pygame.transform.flip(images['boulder'], True, False)
normal = [
    pygame.transform.flip(images['foot'], True, False),
    images['foot']
]

# Function to create shadow effect on images
def shadow(image, shadow_color):
    image = image.convert_alpha()
    img_width, img_height = image.get_size()
    image.lock()
    for x in range(img_width):
        for y in range(img_height):
            color = image.get_at((x, y))
            if color.a != 0:
                image.set_at((x, y), shadow_color + (color.a,))
    image.unlock()
    return image

# Create shadows for specific images
shadows = {
    images['log1']: shadow(images['log1'], (120, 165, 80)),
    images['log2']: shadow(images['log2'], (120, 165, 80)),
    images['boulder']: shadow(images['boulder'], (76, 76, 76)),
    images['fboulder']: shadow(images['fboulder'], (76, 76, 76)),
    images['boulder2']: shadow(images['boulder2'], (76, 76, 76))
}

# Game state variables
stamina = 3000
heat = 150
hoptime = 0
score = 0
locked = 3
walk_radius = [80, 80]
scale = 0
jumps = 0

effects = {
    'slipchance': 0,
    'heat': 0.05,
    'stamina': 0.2
}

platforms = []
decoration = []
footprints = []

stats = {
    'Water': 'Stamina will refill faster',
    'Matress': 'WIP',
    'Sleeping Bag': 'Lets you skip night time',
    'Left Foot': ['Upgrades left footwear', 'Lets you walk further'],
    'Right Foot': ['Upgrades right footwear', 'Lets you walk further'],
    'Clothes': 'Protection from heat'
}

running = True
clicked = False
menu = True
ignore = False
twisted = False
bgcolor = "#000000"
feet = [[WIDTH / 2 - 100, 700], [WIDTH / 2 + 100, 700]]

# Load and play background audio
pygame.mixer.music.load('sounds/ambience.wav')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.05)

sounds = [
    pygame.mixer.Sound('sounds/ow.wav'),
    pygame.mixer.Sound('sounds/jump.wav'),
    pygame.mixer.Sound('sounds/bone.mp3')
]
sounds[0].set_volume(0.1)
sounds[1].set_volume(0.2)

# Hitbox class for collision detection
class Hitbox:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r

# Function to check rectangle-circle intersection
def rect_circle_intersect(rect, circle_center, circle_radius):
    corners = [rect.topleft, rect.topright, rect.bottomleft, rect.bottomright]
    for corner in corners:
        if math.hypot(corner[0] - circle_center[0], corner[1] - circle_center[1]) <= circle_radius:
            return True
    closest_x = max(rect.left, min(circle_center[0], rect.right))
    closest_y = max(rect.top, min(circle_center[1], rect.bottom))
    distance_x = circle_center[0] - closest_x
    distance_y = circle_center[1] - closest_y
    return distance_x ** 2 + distance_y ** 2 <= circle_radius ** 2

# Function to get the closest point on the circle's perimeter
def closest_point_on_circle(pos, locked):
    distance = math.sqrt((pos[0] - feet[locked][0]) ** 2 + (pos[1] - feet[locked][1]) ** 2)
    closest_x = feet[locked][0] + walk_radius[locked] * (pos[0] - feet[locked][0]) / distance
    closest_y = feet[locked][1] + walk_radius[locked] * (pos[1] - feet[locked][1]) / distance
    return [closest_x, closest_y]

# Function to check circle-circle intersection
def circles_intersect(circle1_pos, circle1_radius, circle2_pos, circle2_radius):
    distance = math.sqrt((circle1_pos[0] - circle2_pos[0]) ** 2 + (circle1_pos[1] - circle2_pos[1]) ** 2)
    return distance < circle1_radius + circle2_radius

# Function to display text on the screen
def show_text(text, size, location, color):
    font = pygame.font.Font(None, size)
    rendered_text = font.render(text, True, color)
    text_rect = rendered_text.get_rect(center=location)
    screen.blit(rendered_text, text_rect)

# Function to convert hex color to RGB
def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i + 2], 16) for i in (0, 2, 4))

# Function to apply damage tint on the screen
def damage_tint(surface, scale):
    tint = min(255, max(0, round(255 * (1 - scale))))
    surface.fill((255, tint, tint), special_flags=pygame.BLEND_MIN)

# Function to switch to boulder biome
def biome_boulder():
    global biome, platforms
    biome = 'boulder'
    for i in range(26):
        platform_x = random.randint(100, 400)
        platform_y = i * 50 - 1800
        random_choice = random.randint(0, 2)
        platforms.append({
            "hitbox": Hitbox(platform_x, platform_y, [56, 56, 45][random_choice]),
            "img": [images['boulder'], images['fboulder'], images['boulder2']][random_choice],
            "biome": "boulder",
            "timer": 0
        })
    decoration.append({
        "hitbox": pygame.Rect(0, -1400, 0, 0),
        "img": images['transition1'],
        "biome": "boulder"
    })

# Function to switch to snowy biome
def biome_snowy():
    global biome, footprints
    biome = 'snowy'
    footprints = []
    decoration.append({
        "hitbox": pygame.Rect(0, -1400, 0, 0),
        "img": images['transition2'],
        "biome": "snowy"
    })
    for _ in range(6):
        platform_x = random.randint(0, 400)
        platform_y = random.randint(-20, 800) - 800
        decoration.append({
            "hitbox": pygame.Rect(platform_x, platform_y, 0, 0),
            "img": images['rock'],
            "biome": "snowy"
        })

# Function to switch to grass biome
def biome_grass():
    global biome
    biome = 'grass'
    for _ in range(10):
        platform_x = random.randint(0, 400)
        platform_y = random.randint(-20, 800) - 800
        decoration.append({
            "hitbox": pygame.Rect(platform_x, platform_y, 0, 0),
            "img": images['grass'],
            "biome": "grass"
        })
    decoration.append({
        "hitbox": pygame.Rect(0, -1400, 0, 0),
        "img": images['transition3'],
        "biome": "grass"
    })

# Biome selector based on the game progress
def select_biome():
    biome_choice = random.randint(0, 2)
    if biome_choice == 0:
        biome_boulder()
    elif biome_choice == 1:
        biome_snowy()
    else:
        biome_grass()

# Game main loop
while running:
    screen.fill(hex_to_rgb(bgcolor))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    if menu:
        # Draw menu items
        show_text("Platformer Game", 74, (WIDTH // 2, HEIGHT // 4), (255, 255, 255))
        show_text("Press Space to Start", 36, (WIDTH // 2, HEIGHT // 2), (255, 255, 255))
        show_text("Controls: Use arrow keys to move", 24, (WIDTH // 2, HEIGHT * 3 // 4), (255, 255, 255))
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            menu = False
            select_biome()
    else:
        # Game logic
        for platform in platforms:
            screen.blit(platform["img"], (platform["hitbox"].x, platform["hitbox"].y))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
