import pygame
import math

# Initialize Pygame
pygame.init()

# Define the dimensions of the display surface
width, height = 450, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Hexagon in Pygame')

# Define colors
bg_color = '#007F37'
hexagon_default_color = '#00603E'
hexagon_hover_color = '#00D889'
hexagon_selected_color = '#FFFFFF'
hexagon_outline_color = '#003D26'

# Function to calculate the vertices of a hexagon
def calculate_hexagon_vertices(center, size):
    return [
        (center[0] + size * math.cos(math.radians(60 * i)), 
         center[1] + size * math.sin(math.radians(60 * i)))
        for i in range(6)
    ]

# Function to check if a point is inside a polygon
def point_in_polygon(point, vertices):
    x, y = point
    n = len(vertices)
    inside = False
    p1x, p1y = vertices[0]
    for i in range(n + 1):
        p2x, p2y = vertices[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

# Hexagon properties
hexagons = []
selected = []

hexagon_positions = [
    (135, 347), (315, 347),
    (135, 450), (315, 450),
    (225, 296), (225, 399), (225, 502)
]
hexagon_size = 60

for pos in hexagon_positions:
    vertices = calculate_hexagon_vertices(pos, hexagon_size)
    hexagons.append(vertices)

# State management
def menu():
    running = True
    while running:
        clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True

        screen.fill(bg_color)

        mouse_pos = pygame.mouse.get_pos()
        for i, hexagon in enumerate(hexagons):
            if point_in_polygon(mouse_pos, hexagon):
                if clicked and i not in selected:
                    if len(selected) < 2:
                        selected.append(i)
                color = hexagon_hover_color
            else:
                color = hexagon_default_color

            if i in selected:
                color = hexagon_selected_color

            pygame.draw.polygon(screen, color, hexagon, 0)
            pygame.draw.polygon(screen, hexagon_outline_color, hexagon, 4)

        pygame.display.flip()

        if len(selected) == 2:
            running = False


def game():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                running = False

        screen.fill((0, 64, 0))  # Clear the screen with black color
        # Game logic and drawing goes here

        pygame.display.flip()

# Main loop
current_state = 'menu'

while True:
    if current_state == 'menu':
        menu()
        current_state = 'game'


    elif current_state == 'game':
        game()
        break  # Exit after the game state for this example
