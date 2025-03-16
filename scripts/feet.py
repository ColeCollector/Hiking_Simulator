import pygame, math

from scripts.utils import *
from scripts.platforms import Platform

class Feet():
    def __init__(self, game):
        self.game = game
        self.pos = [[85, 350], [185, 350]]
        self.hitbox = [pygame.Rect(85 - 20, 350 - 40, 40, 80),
                       pygame.Rect(185 - 20, 350 - 40, 40, 80)]
        self.elipse = [[], []]
        self.wet_feet = 0
        self.pos_distance = 0
        self.target = [[85, 350], [185, 350]]
        self.delta = [[0, 0], [0, 0]]
        self.predicted_velocity = 0
        self.selected = -1
        self.collisions = [True, True]
        self.pulling = False
        self.jump_protection = False
        self.pull_pos = ((self.pos[0][0] + self.pos[1][0]) // 2, (self.pos[0][1] + self.pos[1][1]) // 2)
    
    def click(self):
        # If a foot is selected
        if self.selected != -1:
            self.game.pos = avoid_obstacles(closest_point_on_ellipse(self.game.pos, self.elipse[self.selected]), self.game.platforms.obstacles)

        # If a foot is not selected
        else:
            self.distances = [math.hypot(2 * (self.game.pos[0] - foot[0]), self.game.pos[1] - foot[1]) for foot in self.pos]
            # If the click is outside the circle
            if all(not is_within_ellipse(self.game.pos, self.elipse[i]) for i in range(2)):
                if is_within_circle(self.game.pos, self.pull_pos, round(self.edge_distance / 10)) or self.pulling:
                    self.pulling = True
                else:
                    self.selected = self.distances.index(min(self.distances))
                    self.game.pos = closest_point_on_ellipse(self.game.pos, self.elipse[self.selected])
                    
            if not self.pulling:
                self.game.pos = avoid_obstacles(self.game.pos, self.game.platforms.obstacles)
    
    def draw(self, screen):
        # Update Feet
        for i, foot in enumerate(self.pos):

            foot[1] += self.game.speed
            self.target[i][1] += self.game.speed
            
            for Θ in range(2):
                self.delta[Θ][i] = (self.pos[i][Θ] - self.target[i][Θ]) * 0.2
                
                if abs(self.delta[Θ][i]) < 0.1: 
                    self.jump_protection = False
                    self.delta[Θ][i] = 0

                foot[Θ] -= self.delta[Θ][i]
        
        # Draw and calculate slingshot
        p1, p2 = self.pos[0], self.pos[1]

        # Compute the direction vector
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        self.edge_distance= math.sqrt(dx**2 + dy**2)

        dx /= self.edge_distance
        dy /= self.edge_distance

        # Compute edge points
        edge1 = p1
        edge2 = p2

        if not self.pulling:
            self.pull_pos = ((edge1[0] + edge2[0]) // 2, (edge1[1] + edge2[1]) // 2)  # Middle point

        # Draw trajectory if pulling
        else:
            dx = (self.pos[0][0] + self.pos[1][0]) / 2 - self.pull_pos[0]
            dy = (self.pos[0][1] + self.pos[1][1]) / 2 - self.pull_pos[1]

            force = min(math.hypot(dx, dy) / 2, 30)  # Limit force
            angle = math.atan2(dy, dx)
            
            self.predicted_velocity = [math.cos(angle) * force, math.sin(angle) * force]
            trail = calculate_trajectory(self.pull_pos, self.predicted_velocity, self.game.effects['Jump Range'])

            for point in trail:
                pygame.draw.circle(screen, 'white', (int(point[0]), int(point[1])), 3)

        # Draw bending slingshot rubber band
        pygame.draw.line(screen, 'white', edge1, self.pull_pos, 1)
        pygame.draw.line(screen, 'white', edge2, self.pull_pos, 1)
        
        # Defining Collisions with Platforms
        self.collisions = [any(self.game.platforms.collisions[0]), any(self.game.platforms.collisions[1])]

        # Draw Feet
        for i, foot in enumerate(self.pos):
            self.hitbox[i] = pygame.Rect(foot[0] - 15, foot[1] - 35, 30, 70)
            #pygame.draw.rect(self.game.screen, "white", self.hitbox[i], 1)

            self.elipse[i] = pygame.Rect(foot[0] - self.game.walk_range[i] // 2, 
                                        foot[1] - self.game.walk_range[i] - 15, 
                                        self.game.walk_range[i], 
                                        self.game.walk_range[i] * 2)
            
            # Red if not colliding
            if self.collisions[i] or self.game.current_biome in [None, 'snowy', 'beach']: pygame.draw.ellipse(self.game.screen, "white", self.elipse[i], 1)
            else:                  pygame.draw.ellipse(self.game.screen, "red", self.elipse[i], 1)

            # Jumping Animaition
            if self.delta[1][i] != 0: self.game.screen.blit(self.game.images[f'foot_{i + 1}'], (foot[0] - 40, foot[1] - 44))
            else:                     self.game.screen.blit(self.game.images[f'foot_{i + 1}'], (foot[0] - 40, foot[1] - 38))

        # Draw Wet Feet Text
        if self.wet_feet != 0:
            self.wet_feet -= 1
            if self.wet_feet == 0: 
                self.game.effects['Temp'] += 30
            show_text(self.game.screen, "Wet Feet", (80, 106), '#3696BC')
            show_text(self.game.screen, "Wet Feet", (80, 105), '#3ED1DC')

    def handle_event(self):
        if self.pulling:
            self.pulling = False
            self.jump_protection = True

            destination = calculate_trajectory(self.pull_pos, self.predicted_velocity, self.game.effects['Jump Range'])[-1]
            difference = [(self.pos[0][0] + self.pos[1][0]) / 2 - destination[0],
                          (self.pos[0][1] + self.pos[1][1]) / 2 - destination[1]]

            self.game.stamina -= self.game.effects['Fatigue'] * 100
            self.target[0] = avoid_obstacles([self.pos[0][0] - difference[0], self.pos[0][1] - difference[1]], self.game.platforms.obstacles)
            self.target[1] = avoid_obstacles([self.pos[1][0] - difference[0], self.pos[1][1] - difference[1]], self.game.platforms.obstacles)

        elif self.game.mouse_buttons[0]:
            self.game.sounds[1 if self.game.current_biome != 'snowy' else 4].play()

            self.selected = -1  # Unselect the foot
            self.pos_distance = math.sqrt((self.pos[1][0] - self.pos[0][0])**2 + (self.pos[1][1] - self.pos[0][1])**2)
            self.target[self.distances.index(min(self.distances))] = self.game.pos

        self.game.target = 350 - max(self.pos[0][1] - (self.pos[0][1] - self.target[0][1]), self.pos[1][1] - (self.pos[1][1] - self.target[1][1]))
        
    def handle_collisions(self):
        # If we are not on any platform
        if (not self.collisions[0] or not self.collisions[1]) and self.game.current_biome not in ['beach', None] and not self.jump_protection:
            if self.game.current_biome == 'snowy':
                # Add footprints and increase hurt delay in snowy biome
                self.game.positions.append(Platform(self.game, 'snowy', None, [(self.pos[0][0] - 38), (self.pos[0][1] - 38)], shadow(self.game.images['foot_1'], (160, 160, 160)), reset=False))
                self.game.positions.append(Platform(self.game, 'snowy', None, [(self.pos[1][0] - 38), (self.pos[1][1] - 38)], shadow(self.game.images['foot_2'], (160, 160, 160)), reset=False))

                self.game.scale = 200
                self.game.stamina -= self.game.effects['Fatigue'] * 150
            else:
                self.game.scale = 100
                self.game.stamina -= self.game.effects['Fatigue'] * 500

            if self.game.current_biome == 'boulder':
                self.game.sounds[3].play()
                if self.wet_feet == 0:
                    self.game.effects['Temp'] -= 30

                self.wet_feet = 480
            else:
                self.game.sounds[0].play()

        # If feet are too far apart or left foot isnt on the left
        elif self.pos[0][0] > self.pos[1][0] or 180 < self.pos_distance:
            self.game.sounds[2].play()
            self.game.scale = 50
            self.game.stamina -= self.game.effects['Fatigue'] * 300