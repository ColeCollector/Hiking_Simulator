import pygame, math
from _utils import calculate_trajectory

class Feet():
    def __init__(self, game):
        self.game = game
        self.feet = [[85, 350], [185, 350]]
        self.wet_feet = 0

    def set(self, coords, index):
        self.feet[index] = coords

    def slingshot(self, screen):
        p1, p2 = self.feet[0], self.feet[1]
        r1, r2 = self.walk_radius[0] + 1, self.walk_radius[1] + 1  # Account for outline radius

        # Compute the direction vector
        dx, dy = p2[0] - p1[0], p2[1] - p1[1]
        dist = math.sqrt(dx**2 + dy**2)

        if dist > sum(self.game.walk_radius):  # Avoid division by zero
            # Normalize the vector
            dx /= dist
            dy /= dist

            # Compute edge points
            edge1 = (p1[0] + dx * r1, p1[1] + dy * r1)
            edge2 = (p2[0] - dx * r2, p2[1] - dy * r2)

            if not self.game.pulling:
                self.game.pull_pos = ((edge1[0] + edge2[0]) // 2, (edge1[1] + edge2[1]) // 2)  # Middle point

            # Draw trajectory if pulling
            else:
                dx = (self.feet[0][0] + self.feet[1][0]) / 2 - self.game.pull_pos[0]
                dy = (self.feet[0][1] + self.feet[1][1]) / 2 - self.game.pull_pos[1]

                force = min(math.hypot(dx, dy) / 2, 25)  # Limit force
                angle = math.atan2(dy, dx)
                
                predicted_velocity = [math.cos(angle) * force, math.sin(angle) * force]
                trail = calculate_trajectory(self.game.pull_pos, predicted_velocity, self.game.effects['jump'])

                for point in trail:
                    pygame.draw.circle(screen, 'dark gray', (int(point[0]), int(point[1])), 3)

            # Draw bending slingshot rubber band
            pygame.draw.line(screen, 'white', edge1, self.game.pull_pos, 1)
            pygame.draw.line(screen, 'white', edge2, self.game.pull_pos, 1)