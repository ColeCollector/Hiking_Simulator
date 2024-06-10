import pygame, random, playsound

# Initialize Pygame
pygame.init()

#audio
pygame.mixer.init()

#backround audio
pygame.mixer.music.load('ambience.wav')
pygame.mixer.music.play(-1)

jump_sound = pygame.mixer.Sound('jump.wav')

# Screen dimensions
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Platformer Game')

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Player properties
player_width = 50
player_height = 50
player_x = SCREEN_WIDTH // 2
player_y = 0 - player_height
player_velocity = 5
gravity = 1
jump_force = 15
is_jumping = False
vertical_velocity = 0

# Obstacles properties
obstacle_width = 70
obstacle_height = 20
obstacles = []
for i in range(20):
    obstacle_x = random.randint(0, 800)
    obstacle_y = random.randint(0, 500)
    obstacles.append(pygame.Rect(obstacle_x, obstacle_y, obstacle_width, obstacle_height))

# Clock
clock = pygame.time.Clock()
FPS = 60

running = True
while running:
    #playsound.playsound("ambience.wav")
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_a]:
        player_x -= player_velocity

    if keys[pygame.K_d]:
        player_x += player_velocity

    if keys[pygame.K_w] and not is_jumping:
        is_jumping = True
        vertical_velocity = -jump_force
        pygame.mixer.music.load('ambience.wav')
        pygame.mixer.music.play()
        jump_sound.play()


    # Check for collisions with obstacles
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    on_obstacle = False
    for obstacle in obstacles:
        if player_rect.colliderect(obstacle) and vertical_velocity >  0:
            player_y = obstacle.top - player_height
            is_jumping = False
            vertical_velocity = 0
            on_obstacle = True
            break
    
    # Apply gravity if the player is jumping or falling
    if is_jumping or vertical_velocity != 0:
        vertical_velocity += gravity
        player_y += vertical_velocity

    # Check if player has landed on the ground
    if player_y >= SCREEN_HEIGHT - player_height:
        player_y = SCREEN_HEIGHT - player_height
        is_jumping = False
        vertical_velocity = 0
        on_obstacle = True

    # If the player is not on any obstacle or the ground, they should fall
    if not on_obstacle and not is_jumping:
        is_jumping = True
        vertical_velocity = 0

    # Screen boundaries
    if player_x < 0:
        player_x = 0

    if player_x > SCREEN_WIDTH - player_width:
        player_x = SCREEN_WIDTH - player_width

    if player_y == 750:
       running = False

    # Drawing
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, (player_x, player_y, player_width, player_height))

    for obstacle in obstacles:
        pygame.draw.rect(screen, WHITE, obstacle)
        obstacle.y +=1

        if obstacle.y > 800:
            obstacle.y = 0
            obstacle.x = random.randint(0,500)


    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
