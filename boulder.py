import random, math


#THIS IS A PART OF TEST2  - AN ATTEMPT TO CLEAN UP THE CODE IN HIKING.PY   

# Function to check if rectangles are intersecting with circles
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

class Boulder:
    def __init__(self, pos, img, timer):
        self.pos = list(pos)
        self.img = img

    
    def update(self, speed):

        self.pos[1] += speed
        if self.pos[1] > 800:
            self.pos[1] = -400
        
    def render(self, screen):
        screen.blit(self.img, self.pos)
        
        
class Boulders:
    def __init__(self, images):
        self.boulders = []

        for _ in range(26):
            platform_x = random.randint(100,400)
            platform_y = random.randint(0,800)

            randomchoice = random.randint(0,2)
            self.boulders.append(Boulder((platform_x,platform_y), [images['boulder'],images['fboulder'],images['boulder2']][randomchoice], 0))


    def update(self, speed):
        for boulder in self.boulders:
            boulder.update(speed)
    
    def render(self, screen):
        for boulder in self.boulders:
            boulder.render(screen)