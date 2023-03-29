# PLOOM, 0.1 WIP
# Developed by Zain Akram

import sys, math
import json
import pygame, pygame.draw

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

# Transforms point a to be relative player
def translate(point, player):
    return pygame.Vector2(point.x - player.x, point.y - player.y)

# Rotate a point given an angle
def rotate(point, angle):
    return pygame.Vector2(point.x * math.sin(angle) - point.y * math.cos(angle)), (point.x * math.cos(angle) + point.y * math.sin(angle))

# Normalises angle to between -pi and pi
def normalise_angle(angle):
    return angle - (2 * math.pi) * math.floor((angle + math.pi) / (2 * math.pi))

# Calculates intersection point given two segments, returns (None, None) if no intersection
def intersect(line_one_start, line_one_end, line_two_start, line_two_end):
    # When the two lines are parallel or coincident, the denominator is zero.
    d = ((line_one_start.x - line_one_end.x) * (line_two_start.y - line_two_end.y)) - ((line_one_start.y - line_one_end.y) * (line_two_start.x - line_two_end.x))

    # The denominator, d, is checked before calculation to avoid divison by zero error
    if abs(d) < 0.000001: 
        return None

    t = (((line_one_start.x - line_two_start.x) * (line_two_start.y - line_two_end.y)) - ((line_one_start.y - line_two_start.y) * (line_two_start.x - line_two_end.x))) / d
    u = (((line_one_start.x - line_two_start.x) * (line_one_start.y - line_one_end.y)) - ((line_one_start.y - line_two_start.y) * (line_one_start.x - line_one_end.x))) / d

    if t >= 0 and t <= 1 and u >= 0 and u <= 1:
        return pygame.Vector2(line_one_start.x + (t * (line_one_end.x - line_one_start.x)), line_one_start.y + (t * (line_one_end.y - line_one_start.y)))
    else:
        return None

# Transforms position from world space into viewport space
def transform(point, player, angle):
    point = translate(point, player)
    return rotate(point, angle)

# Convert angle in [-(HFOV / 2)..+(HFOV / 2)] to x coordinate
def screen_angle_to_x(angle):
    return int(VIEW_WIDTH // 2 * (1 - math.tan(((angle + (HFOV / 2)) / HFOV) * (math.pi / 2) - (math.pi / 4))))

# -1 right, 0 on, 1 left given a point and a line
def point_side(point, line_start, line_end):
    return math.copysign(1, (line_end.x - line_start.x) * (point.y - line_start.y) - (line_end.y - line_start.y) * (point.x - line_start.x))

# Point is in sector if it is on the right side of all walls
def point_in_sector(point, sector, walls):
    for i in range(sector.num_walls):
        wall_start = walls[sector.start_wall + i]

        # Make sure the sector does not contain any walls from a different sector
        n = sector.start_wall + i + 1
        if n >= sector.start_wall + sector.num_walls:
            n = sector.start_wall
        
        wall_end = walls[n] 

        if point_side(point, wall_start.position, wall_end.position) < 0:
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
    
class Stack:
    def __init__(self, items: list = list()):
        self.__list = items

    def push(self, item):
        self.__list.append(item)

    def pop(self):
        self.__list.pop(-1)

    def peek(self):
        return self.__list[-1]

    def __getitem__(self, index):
        return self.__list[index]
    
    def __len__(self):
         return len(self.__list)
    
class Frustum:
    def __init__(self, angle):
        left = rotate(0, 1, math.pi / 2 - (angle / 2))
        right = rotate(0, 1, math.pi / 2 - (-angle / 2))

        self.near_left = pygame.Vector2(left.x * ZNEAR, left.y * ZNEAR)
        self.far_left = pygame.Vector2(left.x * ZFAR, left.y * ZFAR)
        self.near_right = pygame.Vector2(right.x * ZNEAR, right.y * ZNEAR)
        self.far_right = pygame.Vector2(right.x * ZFAR, right.y * ZFAR)

class Wall:
    def __init__(self, position, next_sector):
        self.position = position
        self.next_sector = next_sector

class Sector:
    def __init__(self, id, start_wall, num_walls, floor, ceiling):
        self.id = id
        self.start_wall = start_wall
        self.num_walls = num_walls
        self.floor = floor
        self.ceiling = ceiling

class Portal:
    def __init__(self, sector_id, start_x, end_x):
        self.sector_id = sector_id
        self.start_x = start_x
        self.end_x = end_x

class Player:
    def __init__(self, position, angle):
        self.position = position
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
                self.position.x += math.cos(self.angle) * SPEED
                self.position.y += math.sin(self.angle) * SPEED

            
            if (keys_down[pygame.K_DOWN] or keys_down[pygame.K_s]):
                self.position.x -= math.cos(self.angle) * SPEED
                self.position.y -= math.sin(self.angle) * SPEED

            # Strafe left and right
            if (keys_down[pygame.K_a]):
                self.position.x += math.sin(self.angle) * SPEED
                self.position.y -= math.cos(self.angle) * SPEED
            
            if (keys_down[pygame.K_d]):
                self.position.x -= math.sin(self.angle) * SPEED
                self.position.y += math.cos(self.angle) * SPEED

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

            if point_in_sector(self.position, sector, walls):
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
        wall = Wall(pygame.Vector2(n["x"], n["y"]), n["nextSector"])
        walls.append(wall)

    num_sectors = len(data["sectors"])

    return sectors, walls, num_sectors

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

    sectors, walls, num_sectors = load_map("content/map.json")
    player = Player(pygame.Vector3(8, 4, 1.65), 0)

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

        pygame.draw.line(target, pygame.Color("red"), (player.position.x * 10, player.position.y * 10), (int(math.cos(player.angle) * 5 + player.position.x * 10), int(math.sin(player.angle) * 5 + player.position.y * 10)))
        target.set_at((int(player.position.x * 10), int(player.position.y * 10)), pygame.Color("green"))

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
                
                pygame.draw.line(target, colour, (p1.position.x*10, p1.position.y*10), (p2.position.x*10, p2.position.y*10))

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