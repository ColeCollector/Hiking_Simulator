import pygame, random, playsound

# Initialize Pygame
pygame.init()

#audio
pygame.mixer.init()

#backround audio

jump_sound = pygame.mixer.Sound('jump.wav')

# Screen dimensions
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Platformer Game')


# Player properties
player_width = 50
player_height = 50
player_x = 0 + player_width
player_y = 0 - player_height


player_velocity = 5
gravity = 1
jump_force = 15
is_jumping = False
vertical_velocity = 0

# Obstacles properties
obstacle_width = 100
obstacle_height = 20
obstacles = []

for i in range(7):
    if random.randint(0,1) == 0: obstacle_x = random.randint(0,100)
    else: obstacle_x = random.randint(350,450)
        
    obstacle_y = i*100
    obstacles.append(pygame.Rect(obstacle_x, obstacle_y, obstacle_width, obstacle_height))

obstacle_height = 500
obstacle_width = 75

obstacle_x = random.randint(200,300)
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
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.key == pygame.K_ESCAPE:
                print("!23")
    player_x, player_y = pygame.mouse.get_pos()
    player_x -= 25
    player_y -= 25


    # Check for collisions with obstacles
    player_rect = pygame.Rect(player_x, player_y, player_width, player_height)
    
    on_obstacle = False
    for obstacle in obstacles:
        if player_rect.colliderect(obstacle):
            print("collision")
            break
    

    # Screen boundaries
    if player_x < 0:
        player_x = 0

    if player_x > SCREEN_WIDTH - player_width:
        player_x = SCREEN_WIDTH - player_width


    # Drawing
    screen.fill("black")
    pygame.draw.rect(screen, "red", (player_x, player_y, player_width, player_height))

    for obstacle in obstacles:
        pygame.draw.rect(screen, "white", obstacle)
        obstacle.y += 1

        
        if obstacle.y > 800:
            obstacle.y = 0
            if obstacle.height < 500:
                if random.randint(0,1) == 0: obstacle.x = random.randint(0,100)
                else: obstacle.x = random.randint(400,500)
            else:
                pass



    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
