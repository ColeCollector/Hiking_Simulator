import pygame, math

# Display Text
def show_text(screen, text, size, location, color):
    size = round(size*0.65)
    font = pygame.font.SysFont('lucidaconsole', size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=location)
    screen.blit(text_surface, text_rect)

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
selected = []
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
        show_text(screen, "PICK TWO", 30, (270/2, 230/2-20), "white")
        show_text(screen, "ITEMS", 30, (270/2, 280/2-20), "white")

        for hexagon in hexagons:
            if hexagons.index(hexagon) in selected:
                color = hexagon_selected_color
                outline = hexagon_selected_outline
                
                if clicked == True and point_in_polygon(pos, hexagon):
                    selected.remove(hexagons.index(hexagon))
                
            elif point_in_polygon(pos, hexagon):
                if clicked == True and len(selected) < 2:
                    selected.append(hexagons.index(hexagon))
                color = hexagon_hover_color
                outline = hexagon_default_outline

            else: 
                color = hexagon_default_color 
                outline = hexagon_default_outline

            # Displaying Hexagons
            pygame.draw.polygon(screen, color, hexagon, 0)
            pygame.draw.polygon(screen, outline, hexagon, 5)
        
        if pygame.Rect(170/2, 676/2+25, 200/2, 50/2).collidepoint(pos):
            #pygame.draw.rect(screen, hexagon_hover_color, (170/2, 676/2, 200/2, 50/2))
            screen.blit(images['button_hover'],(170/2, 676/2+25, 200/2, 50/2))
            if clicked == True and len(selected) == 2:
                # Finding which perk based on which hexagon was selected
                perks = invitems[selected[0]], invitems[selected[1]]

                # Applying the perks
                for perk in perks:
                    if perk == 'Left Foot':
                        walkradius[0] += 2
                        normal[0] = pygame.transform.flip(pygame.image.load('images/boot.png'), True, False)

                    elif perk == 'Right Foot':
                        walkradius[1] += 2
                        normal[1] = pygame.image.load('images/boot.png')
                        #effects['slipchance'] += 1

                    elif perk == 'Water':
                        walkradius[1] -= 3
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
            #pygame.draw.rect(screen, hexagon_default_color, (170/2, 676/2, 200/2, 50/2))
            screen.blit(images['button'],(170/2, 676/2+25, 200/2, 50/2))
            
        show_text(screen, 'DONE', 25, (270/2, 700/2+25), 'white')


        for circle in circles:
            pygame.draw.circle(screen, hexagon_default_outline, circle, 12)

        screen.blit(images['perks'], (0, 0))