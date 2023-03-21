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

FRAMERATE = 60

# Gameplay TODO: Create object to hand state. Needs to be writeable not constants
SENSITIVITY = 0.0024
MULTIPLIER = 31.25
SPEED = 0.4


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
    player = Player(0, 0, 0)

    # Main loop
    is_running = True
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        # Updating TODO: Seperate into single procedure
        player.update()

        # Rendering TODO: Seperate into single procedure
        graphics.fill(pygame.Color("black"))        
        target.fill(CLEAR_COLOR)

        pygame.draw.line(target, pygame.Color("red"), (player.x, player.y), (int(math.cos(player.angle) * 5 + player.x), int(math.sin(player.angle) * 5 + player.y)))
        target.set_at((int(player.x), int(player.y)), pygame.Color("green"))

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