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

''' 
OBJECTIVE 1: Creating map files (also see content/map.json)
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

    # Main loop
    is_running = True
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        # Rendering
        graphics.fill(pygame.Color("black"))        
        target.fill(CLEAR_COLOR)

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