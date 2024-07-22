import pygame
import os

pygame.init()
screen = pygame.display.set_mode((600, 800))
font = pygame.font.Font(None, 36)

# Load backpack image
backpack_image = pygame.image.load(os.path.join('images/backpack.png'))
backpack_rect = backpack_image.get_rect(center=(300, 400))

def draw_ui():
    screen.fill((0, 0, 0))
    screen.blit(backpack_image, backpack_rect)
    y = 100
    for item in items:
        item_text = font.render(f"{item.name}: {item.quantity}", True, (255, 255, 255))
        screen.blit(item_text, (50, y))

        increase_button = pygame.Rect(400, y, 50, 50)
        decrease_button = pygame.Rect(500, y, 50, 50)
        pygame.draw.rect(screen, (0, 255, 0), increase_button)
        pygame.draw.rect(screen, (255, 0, 0), decrease_button)

        plus_text = font.render("+", True, (0, 0, 0))
        minus_text = font.render("-", True, (0, 0, 0))
        screen.blit(plus_text, (415, y))
        screen.blit(minus_text, (515, y))

        y += 100

    pygame.display.flip()


# Load item images (example with water)
water_image = pygame.image.load(os.path.join('images/rock.png'))
water_rect = water_image.get_rect(topleft=(50, 100))




import time

pygame.init()
screen = pygame.display.set_mode((600, 800))
font = pygame.font.Font(None, 36)

# Load backpack image
backpack_image = pygame.image.load(os.path.join('images/backpack.png'))
backpack_rect = backpack_image.get_rect(center=(300, 400))

# Load item images
water_image = pygame.image.load(os.path.join('images/rock.png'))
water_rect = water_image.get_rect(topleft=(50, 100))

# Define other items similarly...

class Item:
    def __init__(self, name, quantity=0):
        self.name = name
        self.quantity = quantity

    def increase(self):
        self.quantity += 1

    def decrease(self):
        if self.quantity > 0:
            self.quantity -= 1

items = [
    Item("Water"),
    Item("Matress"),
    Item("Sleeping Bag"),
    Item("Left Foot"),
    Item("Right Foot"),
    Item("Clothes")
]

def draw_ui():
    screen.fill((0, 0, 0))
    screen.blit(backpack_image, backpack_rect)
    y = 100
    for item in items:
        item_text = font.render(f"{item.name}: {item.quantity}", True, (255, 255, 255))
        screen.blit(item_text, (50, y))

        increase_button = pygame.Rect(400, y, 50, 50)
        decrease_button = pygame.Rect(500, y, 50, 50)
        pygame.draw.rect(screen, (0, 255, 0), increase_button)
        pygame.draw.rect(screen, (255, 0, 0), decrease_button)

        plus_text = font.render("+", True, (0, 0, 0))
        minus_text = font.render("-", True, (0, 0, 0))
        screen.blit(plus_text, (415, y))
        screen.blit(minus_text, (515, y))

        y += 100

    pygame.display.flip()

dragging = None
item_positions = {"water": water_rect.topleft}

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            if water_rect.collidepoint(x, y):
                dragging = 'water'
        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging and backpack_rect.collidepoint(event.pos):
                for item in items:
                    if item.name.lower() == dragging:
                        item.increase()
                dragging = None
                # Animate the item going into the backpack
                item_positions['water'] = backpack_rect.center
                draw_ui()
                screen.blit(water_image, item_positions['water'])
                pygame.display.flip()
                time.sleep(0.5)  # Simple animation delay
                item_positions['water'] = water_rect.topleft
            dragging = None
        elif event.type == pygame.MOUSEMOTION and dragging:
            if dragging == 'water':
                water_rect.move_ip(event.rel)
                item_positions['water'] = water_rect.topleft

    draw_ui()
    screen.blit(water_image, item_positions['water'])
    pygame.display.flip()

pygame.quit()


