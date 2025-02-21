import pygame, math

from scripts.utils import show_text

pygame.mixer.init()
sounds = [pygame.mixer.Sound('data/sounds/select.wav')]
sounds[0].set_volume(0.5)

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
invitems = ['Water', 'Knee Pad', 'Left Foot', 'Right Foot', 'Sleeping Bag', 'Spring', 'Clothes']

class Menu:
    def __init__(self, game):
        self.game = game
        self.game.screen.fill(bg_color)

        for x, hexagon in enumerate(hexagons):
            if selected[x] == 2:
                color = hexagon_selected_color
                outline = 'light blue'
                
                if self.game.clicking == True and point_in_polygon(self.game.pos, hexagon):
                    selected[x] -= 2

            elif selected[x] == 1:
                color = hexagon_selected_color
                outline = hexagon_selected_outline
                
                if self.game.clicking == True and point_in_polygon(self.game.pos, hexagon):
                    if sum(selected.values()) < 3:
                        sounds[0].play()
                        selected[x] += 1

                    elif sum(selected.values()) == 3:
                        selected[x] -= 1
            
            elif point_in_polygon(self.game.pos, hexagon):
                if self.game.clicking == True and sum(selected.values()) < 3:
                    sounds[0].play()
                    selected[x] += 1
                color = hexagon_hover_color
                outline = hexagon_default_outline

            else: 
                color = hexagon_default_color 
                outline = hexagon_default_outline

            # Displaying Hexagons
            pygame.draw.polygon(self.game.screen, color, hexagon, 0)
            pygame.draw.polygon(self.game.screen, outline, hexagon, 5)

            pygame.draw.circle(self.game.screen, outline, circles[x], 12)
        
        if pygame.Rect(85, 363, 100, 25).collidepoint(self.game.pos):
            #pygame.draw.rect(screen, hexagon_hover_color, (170/2, 676/2, 200/2, 50/2))
            self.game.screen.blit(self.game.images['button_hover'], (85, 363, 100, 25))
            if self.game.clicking == True and sum(selected.values()) == 3:
                # Finding which perk based on which hexagon was selected
                perks = {key: value for key, value in selected.items() if value != 0}

                # Applying the perks
                for value in perks:
                    perk = invitems[value]
                    strength = selected[value]

                    if perk == 'Left Foot':
                        self.game.walk_radius[0] += 4 * strength
                        if strength == 1: 
                            self.game.images['foot_1'] = pygame.transform.flip(pygame.image.load('data/images/shoes/croc.png'), True, False)
                            self.game.effects['slipchance'] += 1

                        elif strength == 2: 
                            self.game.images['foot_1'] = pygame.transform.flip(pygame.image.load('data/images/shoes/boot.png'), True, False)

                    elif perk == 'Right Foot':
                        self.game.walk_radius[1] += 4 * strength
                        if strength == 1: 
                            self.game.images['foot_2'] = pygame.image.load('data/images/shoes/croc.png')
                            self.game.effects['slipchance'] += 1

                        elif strength == 2: 
                            self.game.images['foot_2'] = pygame.image.load('data/images/shoes/boot.png')
                        
                    elif perk == 'Water':
                        # + 8 % Regeneration
                        # - 2 Walk Radius
                        self.game.walk_radius[0] -= 2 * strength
                        self.game.walk_radius[1] -= 2 * strength
                        self.game.effects['regen'] += (self.game.effects['regen'] / 8) * strength

                    elif perk == 'Clothes':
                        # + 15°C
                        self.game.effects['temp'] += 15 * strength

                    elif perk == 'Knee Pad':
                        # - 5 % Stamina Reduction
                        self.game.effects['stamina'] -= (self.game.effects['stamina'] / 5) * strength

                    elif perk == 'Sleeping Bag':
                        # Gotta add something here...
                        pass

                    elif perk == 'Spring':
                        if strength == 1:
                            # + 17 % Jump Distance
                            self.game.effects['jump'] += 1

                        elif strength == 2:
                            # + 50 % Jump Distance
                            self.game.effects['jump'] += 3

                self.game.game_status = 'game'
                self.game.effects = self.game.effects
            
        else:
            #pygame.draw.rect(screen, hexagon_default_color, (170/2, 676/2, 200/2, 50/2))
            self.game.screen.blit(self.game.images['button'], (85, 363, 100, 25))
        
        self.game.screen.blit(self.game.images['perks'], (0, 0))

        show_text(self.game.screen, "PICK THREE", (138, 98), hexagon_default_color)
        show_text(self.game.screen, "PICK THREE", (135, 95), "white")

        show_text(self.game.screen, "ITEMS", (138, 123), hexagon_default_color)
        show_text(self.game.screen, "ITEMS", (135, 120), "white")
        show_text(self.game.screen, 'DONE', (135, 375), 'white')
