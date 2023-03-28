# PLOOM, 0.1 WIP
# Developed by Zain Akram

import sys
import math
import json
import pygame
import pygame.draw

# Screen size
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 360
VIEW_WIDTH = 320
VIEW_HEIGHT = 180

CLEAR_COLOR = (pygame.Color("cornflower blue"))

# Engine
FRAMERATE = 60
HFOV = math.radians(103)
VFOV = math.radians(90)
ZNEAR = 0.0001
ZFAR = 100

# Gameplay TODO: Create object to handle state. Needs to be writeable not constants
SENSITIVITY = 0.0024
MULTIPLIER = 31.25
SPEED = 0.04

# -1 right, 0 on, 1 left given a point and a line
def point_side(x, y, ax, ay, bx, by):
    return math.copysign(1, (bx - ax) * (y - ay) - (by - ay) * (x - ax))

# Rotate a point given an angle
def rotate(x, y, angle):
    return (x * math.sin(angle) - y * math.cos(angle)), (x * math.cos(angle) + y * math.sin(angle))

# Transforms point a to be relative player
def translate(ax, ay, px, py):
    return ax - px, ay - py

# Transforms position from world space into viewport space
def world_to_viewport(x, y, px, py, angle):
    x, y = translate(x, y, px, py)
    return rotate(x, y, angle)

# Calculates intersection point given two segments, returns (None, None) if no intersection
def intersect(a1x, a1y, a2x, a2y, b1x, b1y, b2x, b2y):
    # When the two lines are parallel or coincident, the denominator is zero.
    d = ((a1x - a2x) * (b1y - b2y)) - ((a1y - a2y) * (b1x - b2x))

    # The denominator, d, is checked before calculation to avoid divison by zero error
    if abs(d) < 0.000001: 
        return None, None

    t = (((a1x - b1x) * (b1y - b2y)) - ((a1y - b1y) * (b1x - b2x))) / d
    u = (((a1x - b1x) * (a1y - a2y)) - ((a1y - b1y) * (a1x - a2x))) / d

    if t >= 0 and t <= 1 and u >= 0 and u <= 1:
        return a1x + (t * (a2x - a1x)), a1y + (t * (a2y - a1y))
    else:
        return None, None

# Normalises angle to between -pi and pi
def normalise_angle(angle):
    return angle - (2 * math.pi) * math.floor((angle + math.pi) / (2 * math.pi))

# Convert angle in [-(HFOV / 2)..+(HFOV / 2)] to x coordinate
def screen_angle_to_x(angle):
    return int(VIEW_WIDTH // 2 * (1 - math.tan(((angle + (HFOV / 2)) / HFOV) * (math.pi / 2) - (math.pi / 4))))

# Point is in sector if it is on the right side of all walls
def point_in_sector(x, y, sector, walls):
    for i in range(sector.num_walls):
        p1 = walls[sector.start_wall + i]

        # Make sure the sector does not contain any walls from a different sector
        n = sector.start_wall + i + 1
        if n >= sector.start_wall + sector.num_walls:
            n = sector.start_wall
        
        p2 = walls[n] 

        if point_side(x, y, p1.x, p1.y, p2.x, p2.y) < 0:
            return False
    return True

class Queue:
    def __init__(self, items: list = list()):
        self.__list = items

    def enqueue(self, item):
        self.__list.append(item)

    def dequeue(self):
        self.__list.pop(0)

    def peek(self):
        return self.__list[0]

    def __getitem__(self, index):
        return self.__list[index]
    
    def __len__(self):
         return len(self.__list)
    
class Frustum:
    def __init__(self, angle):
        __left_x, __left_y = rotate(0, 1, math.pi / 2 - (angle / 2))
        __right_x, __right_y = rotate(0, 1, math.pi / 2 - (-angle / 2))

        near_left_x, near_left_y = __left_x * ZNEAR, __left_y * ZNEAR
        far_left_x, far_left_y = __left_x * ZFAR, __left_y * ZFAR
        near_right_x, near_right_y = __right_x * ZNEAR, __right_y * ZNEAR
        far_right_x, far_right_y = __right_x * ZFAR, __right_y * ZFAR

class Wall:
    def __init__(self, x, y, next_sector):
        self.x = x
        self.y = y
        self.next_sector = next_sector

class Sector:
    def __init__(self, id, start_wall, num_walls, floor, ceiling):
        self.id = id
        self.start_wall = start_wall
        self.num_walls = num_walls
        self.floor = floor
        self.ceiling = ceiling

class Player:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = math.radians(angle)
        self.sector = 0
        self.__previous_key = pygame.key.get_pressed()

    '''
    OBJECTIVE 9: Update the player's position
    '''

    def update(self):
            # TODO: Multiply by delta time to make speed framerate independent
            mouse_x = pygame.mouse.get_rel()[0]
            keys_down = pygame.key.get_pressed()

            '''
            OBJECTIVE 9.2: Allow for rotation using the mouse
            '''

            # Mouse rotation
            self.angle += mouse_x * SENSITIVITY

            '''
            OBJECTIVE 9.1: Allow for movement backwards and forward and strafing using keyboard keys
            '''

            # Left and right rotation
            if (keys_down[pygame.K_LEFT]):
                self.angle -= SENSITIVITY * MULTIPLIER
            
            if (keys_down[pygame.K_RIGHT]):
                self.angle += SENSITIVITY * MULTIPLIER

            # Backwards and forwards movement
            if (keys_down[pygame.K_UP] or keys_down[pygame.K_w]):
                self.x += math.cos(self.angle) * SPEED
                self.y += math.sin(self.angle) * SPEED

            
            if (keys_down[pygame.K_DOWN] or keys_down[pygame.K_s]):
                self.x -= math.cos(self.angle) * SPEED
                self.y -= math.sin(self.angle) * SPEED

            # Strafe left and right
            if (keys_down[pygame.K_a]):
                self.x += math.sin(self.angle) * SPEED
                self.y -= math.cos(self.angle) * SPEED
            
            if (keys_down[pygame.K_d]):
                self.x -= math.sin(self.angle) * SPEED
                self.y += math.cos(self.angle) * SPEED

            self.__previous_key = keys_down

    def find_sector(self, sectors, walls):
        # Breath Fisrst Traversal is used as player is likely to be in neighbouring sectors
        queue = Queue()
        visited = list()

        visited.append(self.sector)
        queue.enqueue(self.sector)
        found = None

        while len(queue) != 0:
            id = queue.peek()
            queue.dequeue()
            sector = sectors[id]

            if point_in_sector(self.x, self.y, sector, walls):
                found = id
                break

            for i in range(sector.num_walls):
                wall = walls[sector.start_wall + i]
                if wall.next_sector != -1:
                    if wall.next_sector not in visited:
                        visited.append(wall.next_sector)
                        queue.enqueue(wall.next_sector)

        if found == None:
            print("ERROR: Player is not in a sector!")
            self.sector = 0
        else:
            self.sector = found

''' 
OBJECTIVE 1: Creating map files (also see "content/map.json")
'''

def load_map(path):
    sectors = []
    walls = []

    '''
    OBJECTIVE 1.2: Read map files into a workable format
    '''

    with open(path) as file:
        data = json.load(file)

    for i, n in enumerate(data["sectors"]):
        sector = Sector(i, n["startWall"], n["numWalls"], n["floor"], n["ceiling"])
        sectors.append(sector)
    
    for i, n in enumerate(data["walls"]):
        wall = Wall(n["x"], n["y"], n["nextSector"])
        walls.append(wall)

    return sectors, walls

def main():
    # Inintialise pygame
    pygame.init()
    pygame.display.set_caption("PLOOM")
    clock = pygame.time.Clock()

    # Set display mode
    flags = pygame.DOUBLEBUF | pygame.RESIZABLE
    graphics = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
    graphics.set_alpha(None)
    target = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT))

    sectors, walls = load_map("content/map.json")
    player = Player(8, 4, 0)

    # Main loop
    is_running = True
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        # Updating TODO: Seperate into single procedure
        player.update()
        player.find_sector(sectors, walls)

        # Rendering TODO: Seperate into single procedure
        graphics.fill(pygame.Color("black"))        
        target.fill(CLEAR_COLOR)

        pygame.draw.line(target, pygame.Color("red"), (player.x * 10, player.y * 10), (int(math.cos(player.angle) * 5 + player.x * 10), int(math.sin(player.angle) * 5 + player.y * 10)))
        target.set_at((int(player.x * 10), int(player.y * 10)), pygame.Color("green"))

        for sector in sectors:
            for i in range(sector.num_walls):
                p1 = walls[sector.start_wall + i]

                n = sector.start_wall + i + 1
                if n >= sector.start_wall + sector.num_walls:
                    n = sector.start_wall
                
                p2 = walls[n] 

                if p1.next_sector == -1:
                    colour = pygame.Color("black")
                else:
                    colour = pygame.Color("red")
                
                pygame.draw.line(target, colour, (p1.x*10, p1.y*10), (p2.x*10, p2.y*10))

        ''' 
        OBJECTIVE 2: Allow for a scalable window
        '''

        #region Render target resizing

        window_width, window_height = graphics.get_size()
        scale = min(window_width / VIEW_WIDTH, window_height / VIEW_HEIGHT)

        bar_width = int((window_width - int(VIEW_WIDTH * scale)) / 2)
        bar_height = int((window_height - int(VIEW_HEIGHT * scale)) / 2)

        '''
        OBJECTIVE 2.1: Resize all content within window to correct size 
        '''

        resized = pygame.transform.scale(target, (int(VIEW_WIDTH * scale), int(VIEW_HEIGHT * scale)))
        graphics.blit(resized, (bar_width, bar_height))

        #endregion

        pygame.display.update()

        # Cap the framerate at 60 frames per second
        clock.tick(FRAMERATE)
        pygame.display.set_caption("PLOOM, FPS: {}".format(clock.get_fps()))
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()