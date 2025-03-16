import pygame, math, sys

from scripts.utils import show_text

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

class Menu:
    def __init__(self, game):
        pygame.mixer.init()
        self.sounds = [pygame.mixer.Sound('data/sounds/select.wav')]
        self.sounds[0].set_volume(0.5)
        self.game = game
        self.clicking = False

        self.hexagons = []
        self.colours = {
            "dark": '#0B1911',
            "outline": '#163020',
            "mid_green": '#304D30',
            "light_green": '#387738',
            "whiteish": '#EDE9E3',
        }

        self.invitems = {
            'Water' : 0, 
            'Band-Aid' : 0, 
            'Left Foot' : 0, 
            'Right Foot' : 0, 
            'Spring' : 0, 
            'Hat' : 0}
        
        self.circles = []

        for i in range(6):
            coords = (50, 85 + 50 * i)
            self.circles.append(coords)
            self.hexagons.append(calculate_hexagon_vertices(coords, 25))

    def reset(self):
        pygame.mixer.music.pause()

        # Resetting any old menu upgrades
        self.game.default_effects = {
            'Grip'       : 12, 
            'Temp'       : 0, 
            'Regen'      : 0.12, 
            'Fatigue'    : 0.08,
            'Jump Range' : 5
        }

        self.game.walk_range = [50, 50] 
        self.game.images['foot_1'] = pygame.transform.flip(pygame.image.load('data/images/shoes/foot.png'), True, False)
        self.game.images['foot_2'] = pygame.image.load('data/images/shoes/foot.png')

    def run(self):
        # Get mouse position and self.scale it down
        self.pos = list(pygame.mouse.get_pos())
        self.pos[0] /= 2
        self.pos[1] /= 2

        self.game.screen.fill(self.colours['dark'])
        self.handle_events()

        for x, hexagon in enumerate(self.hexagons):
            key = list(self.invitems.keys())[x]

            pygame.draw.rect(self.game.screen, self.colours['outline'], (140 - 200 // 2, 85 + x * 50 - 15, 200, 30))
            show_text(self.game.screen, key, (140, 86 + x * 50), self.colours['mid_green'])
            show_text(self.game.screen, key, (140, 85 + x * 50), 'white')
            
            if self.invitems[key] == 2:
                color = self.colours['whiteish']
                outline = 'light blue'
                
                if self.clicking == True and point_in_polygon(self.pos, hexagon):
                    self.invitems[key] -= 2

            elif self.invitems[key] == 1:
                color = self.colours['whiteish']
                # Yelow/Orange Colour
                outline = '#E8AF66'
                
                if self.clicking == True and point_in_polygon(self.pos, hexagon):
                    if sum(self.invitems.values()) < 5:
                        self.sounds[0].play()
                        self.invitems[key] += 1

                    elif sum(self.invitems.values()) == 5:
                        self.invitems[key] -= 1
            
            elif point_in_polygon(self.pos, hexagon):
                if self.clicking == True and sum(self.invitems.values()) < 5:
                    self.sounds[0].play()
                    self.invitems[key] += 1
                color = self.colours['light_green']
                outline = self.colours['outline']

            else: 
                color = self.colours['mid_green'] 
                outline = self.colours['outline']

            # Displaying Hexagons
            pygame.draw.polygon(self.game.screen, color, hexagon, 0)
            pygame.draw.polygon(self.game.screen, outline, hexagon, 5)
            pygame.draw.circle(self.game.screen, outline, self.circles[x], 12)

        if pygame.Rect(85, 440, 100, 25).collidepoint(self.pos):
            self.game.screen.blit(self.game.images['button_hover'], (85, 440, 100, 25))
            if self.clicking == True and sum(self.invitems.values()) == 5:
                self.apply_perks()
        else:
            self.game.screen.blit(self.game.images['button'], (85, 440, 100, 25))

        self.game.screen.blit(self.game.images['perks'], (0, 0))
        if sum(self.invitems.values()) == 2:
            show_text(self.game.screen, f"YOU HAVE 1 CREDIT", (135, 33), "white")
        else:
            show_text(self.game.screen, f"YOU HAVE {5 - sum(self.invitems.values())} CREDITS", (135, 33), "white")
        show_text(self.game.screen, 'DONE', (135, 452), 'white')

        pygame.draw.rect(self.game.screen, self.colours['mid_green'], (135 - 240 // 2, 400 - 30, 240, 60))
        pygame.draw.rect(self.game.screen, self.colours['outline'], (135 - 230 // 2, 400 - 25, 230, 50))
        
        self.stats = self.calculate_effects(False)
        show_text(self.game.screen, f"Regen   : {round(self.stats['Regen'] * 60, 2)}/s   Fatigue     : {round(self.stats['Fatigue'], 2)}", (135, 390), 'white')
        show_text(self.game.screen, f"Jump Range : {self.stats['Jump Range'] }   Temp Boost  : {self.stats['Temp']}°C", (135, 410), 'white')
        
        self.game.display.blit(pygame.transform.scale(self.game.screen, self.game.display.get_size()), (0, 0))
        pygame.display.flip()
        self.game.clock.tick(60)

    def calculate_effects(self, save):
        temp_effects = self.game.default_effects.copy()

        for perk in self.invitems:
            strength = self.invitems[perk]

            if perk == 'Left Foot':
                if strength == 1: 
                    temp_effects['Grip'] -= 1

            elif perk == 'Right Foot':
                if strength == 1: 
                    temp_effects['Grip'] -= 1
                
            elif perk == 'Water':
                # + 8 % Regeneration
                # - 2 Walk Radius
                temp_effects['Regen'] += (temp_effects['Regen'] / 8) * strength

            elif perk == 'Hat':
                # + 15°C
                temp_effects['Temp'] += 15 * strength

            elif perk == 'Band-Aid':
                # - 5 % Fatigue Reduction
                temp_effects['Fatigue'] -= (temp_effects['Fatigue'] / 5) * strength

            elif perk == 'Spring':
                if strength == 1:
                    # + 17 % Jump Range
                    temp_effects['Jump Range'] += 1

                elif strength == 2:
                    # + 50 % Jump Range
                    temp_effects['Jump Range'] += 3

        if save:
            self.game.default_effects = temp_effects

        return temp_effects

    def apply_perks(self):
        # Applying the perks
        for perk in self.invitems:
            strength = self.invitems[perk]

            if perk == 'Left Foot':
                self.game.walk_range[0] += 4 * strength
                if strength == 1: 
                    self.game.images['foot_1'] = self.game.images['croc_flipped']

                elif strength == 2: 
                    self.game.images['foot_1'] = self.game.images['boot_flipped']

            elif perk == 'Right Foot':
                self.game.walk_range[1] += 4 * strength
                if strength == 1: 
                    self.game.images['foot_2'] = self.game.images['croc']

                elif strength == 2: 
                    self.game.images['foot_2'] = self.game.images['boot']
                
            elif perk == 'Water':
                # + 8 % Regeneration
                # - 2 Walk Radius
                self.game.walk_range[0] -= 2 * strength
                self.game.walk_range[1] -= 2 * strength
        
        self.calculate_effects(True)
        self.game.game_status = 'game'
        self.game.reset()
        pygame.mixer.music.unpause()

    def handle_events(self):
        self.clicking = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.clicking = True