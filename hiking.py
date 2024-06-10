from game import SCREEN_HEIGHT
import pygame
height = 800
width = 500
# pygame setup
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
running = True

while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pos = pygame.mouse.get_pos()
    print(pos)
    # fill the screen with a color to wipe away anything from last frame
    screen.fill("purple")
    pygame.draw.circle(screen,"red",pos,20)
    # RENDER YOUR GAME HERE

    # flip() the display to put your work on screen
    pygame.display.flip()

    clock.tick(60)  # limits FPS to 60

pygame.quit()