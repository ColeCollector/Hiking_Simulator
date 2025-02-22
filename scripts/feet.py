import pygame, math

from scripts.utils import *
from scripts.platforms import Platform

class Feet():
    def __init__(self, game):
        self.game = game
        self.pos = [[85, 350], [185, 350]]
        self.pos_distance = 0
        self.hitbox = [pygame.Rect(85 - 20, 350 - 40, 40, 80),
                       pygame.Rect(185 - 20, 350 - 40, 40, 80)]
        self.wet_feet = 0
        self.predicted_velocity = 0
        self.selected = -1
        self.pulling = False
        self.pull_pos = ((self.pos[0][0] + self.pos[1][0]) // 2, (self.pos[0][1] + self.pos[1][1]) // 2)
    
    def click(self):
        if self.selected != -1:  # If a foot is selected
            self.game.pos = avoid_obstacles(closest_point_on_circle(self.game.pos, self.pos[self.selected], self.game.walk_radius[self.selected]), self.game.platforms.obstacles)

        else:  # If a foot is not selected
            self.distances = [math.hypot(self.game.pos[0] - foot[0], self.game.pos[1] - foot[1]) for foot in self.pos]
            # If the click is outside the circle
            if all(dist > self.game.walk_radius[i] for i, dist in enumerate(self.distances)):
                if is_within_circle(self.game.pos, self.pull_pos, round(self.edge_distance/ 15)) or self.pulling:
                    self.pulling = True
                else:
                    self.selected = self.distances.index(min(self.distances))
                    self.game.pos = closest_point_on_circle(self.game.pos, self.pos[self.selected], self.game.walk_radius[self.selected])
                    
            if not self.pulling:
                self.game.pos = avoid_obstacles(self.game.pos, self.game.platforms.obstacles)

    def draw(self, screen):
        # Update Feet
        for i, foot in enumerate(self.pos):
            foot[1] += round(self.game.speed)
        
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

            force = min(math.hypot(dx, dy) / 2, 25)  # Limit force
            angle = math.atan2(dy, dx)
            
            self.predicted_velocity = [math.cos(angle) * force, math.sin(angle) * force]
            trail = calculate_trajectory(self.pull_pos, self.predicted_velocity, self.game.effects['jump'])

            for point in trail:
                pygame.draw.circle(screen, 'dark gray', (int(point[0]), int(point[1])), 3)

        # Draw bending slingshot rubber band
        pygame.draw.line(screen, 'white', edge1, self.pull_pos, 1)
        pygame.draw.line(screen, 'white', edge2, self.pull_pos, 1)

        # Draw Feet
        for i, foot in enumerate(self.pos):
            pygame.draw.circle(self.game.screen, "white", foot, self.game.walk_radius[i], 1)
            
            self.hitbox[i] = pygame.Rect(foot[0] - 20, foot[1] - 40, 40, 80)
            #pygame.draw.rect(self.game.screen, "white", self.hitbox[i], 1)
            
            self.game.screen.blit(self.game.images[f'foot_{i + 1}'], (foot[0] - 38, foot[1] - 38))
        # Draw Wet Feet Text
        if self.wet_feet != 0:
            self.wet_feet -= 1
            if self.wet_feet == 0: 
                self.game.effects['temp'] += 30
            show_text(self.game.screen, "Wet Feet", (80, 106), '#3696BC')
            show_text(self.game.screen, "Wet Feet", (80, 105), '#3ED1DC')

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.game.clicking = True
            if self.pulling:
                self.pulling = False
                destination = calculate_trajectory(self.pull_pos, self.predicted_velocity, self.game.effects['jump'])[-1]

                self.game.speed = (350 - max(self.pos[0][1], self.pos[1][1])) / 5
                difference = min(self.pos[0][1] - destination[1], self.pos[1][1] - destination[1])

                self.pos[0] = avoid_obstacles([self.pos[0][0], self.pos[0][1] - difference - self.game.walk_radius[0]], self.game.platforms.obstacles)
                self.pos[1] = avoid_obstacles([self.pos[1][0], self.pos[1][1] - difference - self.game.walk_radius[1]], self.game.platforms.obstacles)

            elif self.game.game_status == 'game' and self.game.mouse_buttons[0]:
                self.game.sounds[1 if self.game.current_biome != 'snowy' else 4].play()
                self.game.speed = (350 - max(self.pos[0][1], self.pos[1][1])) / 15

                self.selected = -1  # Unselect the foot
                self.pos_distance = math.sqrt((self.pos[1][0] - self.pos[0][0])**2 + (self.pos[1][1] - self.pos[0][1])**2)
                self.pos[self.distances.index(min(self.distances))] = list(self.game.pos)

        elif self.pulling:
            self.pull_pos = list(event.pos)
            self.pull_pos[0] /= 2
            self.pull_pos[1] /= 2
        

    def handle_collisions(self):
        # If we are not on any platform
        if (not any(self.game.platforms.collisions[0]) or not any(self.game.platforms.collisions[1])) and self.game.current_biome not in ['beach', None]:
            if self.game.current_biome == 'snowy':
                # Add footprints and increase hurt delay in snowy biome
                self.game.positions.append(Platform(self.game, 'snowy', None, [(self.pos[0][0] - 38), (self.pos[0][1] - 38)], shadow(self.game.images['foot_1'], (160, 160, 160)), reset=False))
                self.game.positions.append(Platform(self.game, 'snowy', None, [(self.pos[1][0] - 38), (self.pos[1][1] - 38)], shadow(self.game.images['foot_2'], (160, 160, 160)), reset=False))

                self.game.scale = 200
                self.game.stamina -= self.game.effects['stamina'] * 150
            else:
                self.game.scale = 100
                self.game.stamina -= self.game.effects['stamina'] * 500

            if self.game.current_biome == 'boulder':
                self.game.sounds[3].play()
                if self.wet_feet == 0:
                    self.game.effects['temp'] -= 30

                self.wet_feet = 480
            else:
                self.game.sounds[0].play()

        # If feet are too far apart or left foot isnt on the left
        elif self.pos[0][0] > self.pos[1][0] or 180 < self.pos_distance:
            self.game.sounds[2].play()
            self.game.scale = 50
            self.game.stamina -= self.game.effects['stamina'] * 300