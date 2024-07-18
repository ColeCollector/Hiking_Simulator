import pygame

class Item:
    def __init__(self, name, quantity=0):
        self.name = name
        self.quantity = quantity

    def increase(self):
        if self.quantity < 3:
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

pygame.init()
screen = pygame.display.set_mode((600, 800))
font = pygame.font.Font(None, 36)

def draw_ui():
    screen.fill((0, 0, 0))
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

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            y_pos = 100
            for item in items:
                if 400 <= x <= 450 and y_pos <= y <= y_pos + 50:
                    if sum([item.quantity for item in items]) < 3:
                        item.increase()
                elif 500 <= x <= 550 and y_pos <= y <= y_pos + 50:
                    item.decrease()
                y_pos += 100

    draw_ui()



pygame.quit()
