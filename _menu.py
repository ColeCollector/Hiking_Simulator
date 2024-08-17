import pygame, math
from _utils import show_text

# Calculate the vertices of a hexagon
def calculate_hexagon_vertices(center, size):
    return [
        (center[0] + size * math.cos(math.radians(60 * i)), 
         center[1] + size * math.sin(math.radians(60 * i)))
        for i in range(6)
    ]

# Check if a point is inside a polygon
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

# Define colors
bg_color = '#0B1911'
hexagon_default_color = '#304D30'
hexagon_hover_color = '#387738'
hexagon_selected_color = '#EDE9E3'
hexagon_selected_outline = '#E8AF66'
hexagon_default_outline = '#163020'

# Hexagon properties
hexagons = []
selected = {0:0, 1:0 , 2:0 , 3:0 , 4:0 , 5:0 , 6:0}
circles = []

for i in range(2):
    coords = (i*116 + 77, 213)
    circles.append(coords)
    vertices = calculate_hexagon_vertices(coords, 35)
    hexagons.append(vertices)

for i in range(2):
    coords = (i*116 + 77, 281)
    circles.append(coords)
    vertices = calculate_hexagon_vertices(coords, 35)
    hexagons.append(vertices)

for i in range(3):
    coords = (135, 179 + 68*i)
    circles.append(coords)
    vertices = calculate_hexagon_vertices(coords, 35)
    hexagons.append(vertices)

#invitems = {"Water" : ["plastic bottle", "metal bottle", "water jug"], "Knee-pad" : None, "Left Foot":["crocs", "hiking boots", "work boots"], "Right Foot":["crocs", "hiking boots", "work boots"], "Sleeping Bag":["light bag(10C)", "3 season bag(-5C)", "winter bag(-40)"], "Locked_2" : None, "Clothes":["no spare clothes", "an extra of everything", "7 days of clothes"]}
invitems = ['Water', 'Knee Pad', 'Left Foot', 'Right Foot', 'Sleeping Bag', 'Locked', 'Clothes']

effects = {
    'slipchance' : 0, 
    'heat'       : 0.05, 
    'regen'      : 0.06, 
    'stamina'    : 0.04
}


class Menu:
    def __init__(self, screen, clicked, pos, walkradius, normal, images):
        screen.fill(bg_color)
        self.game_status = 'menu'
        self.effects = effects

        #screen.blit(images['backpack'], (30, 100))
        show_text(screen, "PICK TWO", 30, (135, 95), "white")
        show_text(screen, "ITEMS", 30, (135, 120), "white")

        for x, hexagon in enumerate(hexagons):
            if selected[x] == 2:
                color = hexagon_selected_color
                outline = 'light blue'
                
                if clicked == True and point_in_polygon(pos, hexagon):
                    selected[x] -= 2

            elif selected[x] == 1:
                color = hexagon_selected_color
                outline = hexagon_selected_outline
                
                if clicked == True and point_in_polygon(pos, hexagon):
                    if sum(selected.values()) < 3:
                        selected[x] += 1

                    elif sum(selected.values()) == 3:
                        selected[x] -= 1
            
            elif point_in_polygon(pos, hexagon):
                if clicked == True and sum(selected.values()) < 3:
                    selected[x] += 1
                color = hexagon_hover_color
                outline = hexagon_default_outline

            else: 
                color = hexagon_default_color 
                outline = hexagon_default_outline

            # Displaying Hexagons
            pygame.draw.polygon(screen, color, hexagon, 0)
            pygame.draw.polygon(screen, outline, hexagon, 5)

            pygame.draw.circle(screen, outline, circles[x], 12)
        
        if pygame.Rect(85, 363, 100, 25).collidepoint(pos):
            #pygame.draw.rect(screen, hexagon_hover_color, (170/2, 676/2, 200/2, 50/2))
            screen.blit(images['button_hover'], (85, 363, 100, 25))
            if clicked == True and sum(selected.values()) == 3:
                # Finding which perk based on which hexagon was selected
                perks = {key: value for key, value in selected.items() if value != 0}

                # Applying the perks
                for value in perks:
                    perk = invitems[value]
                    strength = selected[value]

                    if perk == 'Left Foot':
                        walkradius[0] += 2 * strength
                        if strength == 1: 
                            normal[0] = pygame.transform.flip(pygame.image.load('images/croc.png'), True, False)
                            effects['slipchance'] += 1

                        elif strength == 2: 
                            normal[0] = pygame.transform.flip(pygame.image.load('images/boot.png'), True, False)

                    elif perk == 'Right Foot':
                        walkradius[1] += 3 * strength
                        if strength == 1: 
                            normal[1] = pygame.image.load('images/croc.png')
                            effects['slipchance'] += 1

                        elif strength == 2: 
                            normal[1] = pygame.image.load('images/boot.png')
                        
                    elif perk == 'Water':
                        walkradius[0] -= 2 * strength
                        walkradius[1] -= 2 * strength
                        effects['regen'] += 0.02 * strength

                    elif perk == 'Clothes':
                        # First gives 80 % less damage from heat, 
                        # Second gets rid of heat damage
                        effects['heat'] -= min(0.04 * strength, 0.05)

                    elif perk == 'Knee Pad':
                        effects['stamina'] -= 0.005 * strength

                    elif perk == 'Sleeping Bag':
                        # Gotta add something here...
                        pass

                self.game_status = 'game'
                self.effects = effects
            
        else:
            #pygame.draw.rect(screen, hexagon_default_color, (170/2, 676/2, 200/2, 50/2))
            screen.blit(images['button'], (85, 363, 100, 25))
            
        show_text(screen, 'DONE', 25, (135, 375), 'white')

        screen.blit(images['perks'], (0, 0))