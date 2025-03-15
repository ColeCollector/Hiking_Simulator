import pygame, math

def shadow(image, shadowc):
    image = image.convert_alpha()
    imgwidth, imgheight = image.get_size()
    image.lock()

    # Iterate over each pixel
    for x in range(imgwidth):
        for y in range(imgheight):
            color = image.get_at((x, y))
            if color.a != 0:
                image.set_at((x, y), shadowc + (color.a, ))

    # Unlock the surface
    image.unlock()
    return image

def closest_point_on_ellipse(pos, rect):
    center = rect.center
    width, height = rect.width / 2, rect.height / 2  # Semi-axes of the ellipse

    dx = pos[0] - center[0]
    dy = pos[1] - center[1]
    
    # Normalize the distances
    norm_dx = dx / width
    norm_dy = dy / height
    
    # Find the distance to the point on the ellipse
    distance = math.sqrt(norm_dx**2 + norm_dy**2)

    # Ensure the point lies on the ellipse by scaling to the boundary
    ratio = 1 / distance if distance != 0 else 0  # Prevent division by zero

    closest_x = center[0] + norm_dx * ratio * width
    closest_y = center[1] + norm_dy * ratio * height

    return [closest_x, closest_y]

def closest_point_on_circle(pos, center, radius):
    dx = pos[0] - center[0]
    dy = pos[1] - center[1]
    distance = math.sqrt(dx * dx + dy * dy)
    ratio = radius / distance
    closest_x = center[0] + dx * ratio
    closest_y = center[1] + dy * ratio
    return [closest_x, closest_y]

def is_within_ellipse(pos, rect):
    center = rect.center
    a, b = rect.width / 2, rect.height / 2  # Semi-axes of the ellipse
    
    dx = (pos[0] - center[0]) / a
    dy = (pos[1] - center[1]) / b

    return dx**2 + dy**2 <= 1

def is_within_circle(pos, center, radius):
    dx = pos[0] - center[0]
    dy = pos[1] - center[1]
    return dx * dx + dy * dy < radius * radius

def avoid_obstacles(pos, obstacles):
    for obstacle in obstacles:
        if is_within_circle(pos, (obstacle.pos[0] + 80, obstacle.pos[1] + 80), 80):
            pos = closest_point_on_circle(pos, (obstacle.pos[0] + 80, obstacle.pos[1] + 80), 80)
    return pos

def show_text(screen, text, location, color, size=16):
    font = pygame.font.Font('data/font/Alkhemikal.ttf', size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=location)
    screen.blit(text_surface, text_rect)

def damage_tint(surface, scale):
    a = min(255, max(0, round(255 * (1-scale))))
    surface.fill((255, a, a), special_flags = pygame.BLEND_MIN)

def rect_circle_intersect(rect, circle_center, circle_radius):
    #Check if any corner of the rectangle is inside the circle
    corners = [
        rect.topleft, 
        rect.topright, 
        rect.bottomleft, 
        rect.bottomright
    ]
    for corner in corners:
        if math.hypot(corner[0] - circle_center[0], corner[1] - circle_center[1]) <= circle_radius:
            return True

    #Check if any edge of the circle intersects with any edge of the rectangle
    closest_x = max(rect.left, min(circle_center[0], rect.right))
    closest_y = max(rect.top, min(circle_center[1], rect.bottom))
    distance_x = circle_center[0] - closest_x
    distance_y = circle_center[1] - closest_y
    return distance_x ** 2 + distance_y ** 2 <= circle_radius ** 2

def circles_intersect(circle1_pos, circle1_radius, circle2_pos, circle2_radius):
    # Calculate the distance between the centers of the circles
    distance = math.sqrt((circle1_pos[0] - circle2_pos[0])**2 + (circle1_pos[1] - circle2_pos[1])**2)

    # Check if the distance is less than the sum of the radii
    if distance < circle1_radius + circle2_radius: 
        return True
    return False

def calculate_trajectory(start_pos, velocity, frame_count):
    #Returns a list of points representing the trajectory of the shoes
    points = []
    temp_pos = list(start_pos)
    temp_vel = list(velocity)

    for _ in range(frame_count):  # Simulate frame_count frames into the future
        temp_pos[0] += temp_vel[0]
        temp_pos[1] += temp_vel[1]
        points.append(tuple(temp_pos))
    
    return points