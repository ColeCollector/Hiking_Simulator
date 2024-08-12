import pygame, math

# Display Text
def show_text(screen, text, size, location, color):
    a1 = pygame.font.Font(None, size).render(text, True, color)
    a2 = a1.get_rect(center=location) 
    screen.blit(a1, a2)

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
hexagon_selected_color = '#EEF0E5'
hexagon_outline_color = '#163020'

# Hexagon properties
hexagons = []
selected = []

for i in range(2):
    vertices = calculate_hexagon_vertices(((i*180 + 180)/2, 428/2), 26)
    hexagons.append(vertices)

for i in range(2):
    vertices = calculate_hexagon_vertices(((i*180 + 180)/2, 532/2), 26)
    hexagons.append(vertices)

for i in range(3):
    vertices = calculate_hexagon_vertices((270/2, (378 + 104*i)/2), 26)
    hexagons.append(vertices)

invitems = {"Water" : ["plastic bottle", "metal bottle", "water jug"], "Sleeping Bag":["light bag(10C)", "3 season bag(-5C)", "winter bag(-40)"], "Left Foot":["crocs", "hiking boots", "work boots"], "Right Foot":["crocs", "hiking boots", "work boots"], "Locked_1" : None, "Locked_2" : None, "Clothes":["no spare clothes", "an extra of everything", "7 days of clothes"]}
invitems = list(invitems.keys())

effects = {
    'slipchance' : 0, 
    'heat'       : 0.05, 
    'stamina'    : 0.05
}


class Menu:
    def __init__(self, screen, clicked, pos, walkradius, normal, images):
        screen.fill(bg_color)
        self.game_status = 'menu'
        self.effects = effects

        #screen.blit(images['backpack'], (30, 100))
        show_text(screen, "PICK TWO", 30, (270/2, 230/2), "white")
        show_text(screen, "ITEMS", 30, (270/2, 280/2), "white")

        for hexagon in hexagons:
            if hexagons.index(hexagon) in selected:
                color = hexagon_selected_color
                if clicked == True and point_in_polygon(pos, hexagon):
                    selected.remove(hexagons.index(hexagon))
                
            elif point_in_polygon(pos, hexagon):
                if clicked == True and len(selected) < 2:
                    selected.append(hexagons.index(hexagon))
                color = hexagon_hover_color

            else: color = hexagon_default_color 

            # Displaying Hexagons
            pygame.draw.polygon(screen, color, hexagon, 0)
            pygame.draw.polygon(screen, hexagon_outline_color, hexagon, 4)
        
        if pygame.Rect(170/2, 676/2, 200/2, 50/2).collidepoint(pos):
            pygame.draw.rect(screen, hexagon_hover_color, (170/2, 676/2, 200/2, 50/2))
            if clicked == True and len(selected) == 2:
                # Finding which perk based on which hexagon was selected
                perks = invitems[selected[0]], invitems[selected[1]]

                # Applying the perks
                for perk in perks:
                    if perk == 'Left Foot':
                        walkradius[0] += 5
                        normal[0] = pygame.transform.flip(pygame.image.load('images/boot.png'), True, False)

                    elif perk == 'Right Foot':
                        walkradius[1] += 8
                        normal[1] = pygame.image.load('images/croc.png')
                        effects['slipchance'] += 1

                    elif perk == 'Water':
                        effects['stamina'] -= 0.01

                    elif perk == 'Clothes':
                        effects['heat'] -= 0.02

                    elif perk == 'Sleeping Bag':
                        pass

                self.game_status = 'game'
                self.effects = effects

                #shadows[normal[0]] = shadow(normal[0], (22, 22, 22))
                #shadows[normal[1]] = shadow(normal[1], (22, 22, 22))
            
        else:
            pygame.draw.rect(screen, hexagon_default_color, (170/2, 676/2, 200/2, 50/2))
        show_text(screen, 'DONE', 25, (270/2, 700/2), 'white')

        screen.blit(images['perks'], (44/2, 22/2))