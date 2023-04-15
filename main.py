# PLOOM, 0.2 WIP
# Developed by Zain Akram

import sys, math, time
import pygame, pygame.draw
import json

from settings import SETTINGS
from utility import *
    
class Frustum:
    def __init__(self, angle):
        left = rotate(pygame.Vector2(0, 1), math.pi / 2 - (angle / 2))
        right = rotate(pygame.Vector2(0, 1), math.pi / 2 - (-angle / 2))

        znear = SETTINGS["znear"]
        zfar = SETTINGS["zfar"]

        self.near_left = pygame.Vector2(left.x * znear, left.y * znear)
        self.far_left = pygame.Vector2(left.x * zfar, left.y * zfar)
        self.near_right = pygame.Vector2(right.x * znear, right.y * znear)
        self.far_right = pygame.Vector2(right.x * zfar, right.y * zfar)

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

    def update(self, delta_time):
            mouse_x = pygame.mouse.get_rel()[0]
            keys_down = pygame.key.get_pressed()

            '''
            OBJECTIVE 9.2: Allow for rotation using the mouse
            '''

            sensitivity = SETTINGS["sensitivity"]
            sensitivity_multiplier = SETTINGS["sensitivityMultiplier"]
            player_speed = SETTINGS["playerSpeed"]

            # Mouse rotation
            if (pygame.event.get_grab()):
                self.angle += mouse_x * sensitivity

            '''
            OBJECTIVE 9.1: Allow for movement backwards and forward and strafing using keyboard keys
            '''

            # Left and right rotation
            if (keys_down[pygame.K_LEFT]):
                self.angle -= sensitivity * sensitivity_multiplier
            if (keys_down[pygame.K_RIGHT]):
                self.angle += sensitivity * sensitivity_multiplier

            # Backwards and forwards movement
            if (keys_down[pygame.K_UP] or keys_down[pygame.K_w]):
                self.position.x += math.cos(self.angle) * player_speed * delta_time
                self.position.y += math.sin(self.angle) * player_speed * delta_time

            
            if (keys_down[pygame.K_DOWN] or keys_down[pygame.K_s]):
                self.position.x -= math.cos(self.angle) * player_speed * delta_time
                self.position.y -= math.sin(self.angle) * player_speed * delta_time

            # Strafe left and right
            if (keys_down[pygame.K_a]):
                self.position.x += math.sin(self.angle) * player_speed * delta_time
                self.position.y -= math.cos(self.angle) * player_speed * delta_time
            
            if (keys_down[pygame.K_d]):
                self.position.x -= math.sin(self.angle) * player_speed * delta_time
                self.position.y += math.cos(self.angle) * player_speed * delta_time

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
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()

    # Set display mode
    flags = pygame.DOUBLEBUF | pygame.RESIZABLE
    graphics = pygame.display.set_mode((SETTINGS["windowWidth"], SETTINGS["windowHeight"]), flags)
    graphics.set_alpha(None)
    target = pygame.Surface((SETTINGS["viewWidth"], SETTINGS["viewHeight"]))
    pygame.event.set_grab(True)

    prev_time = time.time()
    delta_time = 0

    sectors, walls, num_sectors = load_map("content/map.json")
    player = Player(pygame.Vector3(8, 4, 0), 0)

    # Main loop
    is_running = True
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mouse.set_visible(not(pygame.mouse.get_visible()))
                    pygame.event.set_grab(not(pygame.event.get_grab()))

        # Calculate the interval in seconds from the last frame to the current one
        current_time = time.time()
        delta_time = current_time - prev_time
        prev_time = current_time

        viewWidth = SETTINGS["viewWidth"]
        viewHeight = SETTINGS["viewHeight"]

        hfov = SETTINGS["hfov"]
        vfov = SETTINGS["vfov"]

        # Updating TODO: Seperate into single procedure
        player.update(delta_time)
        player.find_sector(sectors, walls)
        player.position.z = sectors[player.sector].floor + SETTINGS["playerHeight"]

        # Rendering TODO: Seperate into single procedure
        graphics.fill(pygame.Color("black"))
        target.fill(SETTINGS["clearColour"])

        #region Render walls

        # Keep track of whether or not a sector has been drawn
        rendered_sectors = [False for i in range(num_sectors)]

        # Keep track of where on the screen a portal is for each x value
        y_bottom = [0 for i in range(viewWidth)]
        y_top = [viewWidth - 1 for i in range(viewWidth)]
        
        # Create the view frustum
        frustum = Frustum(hfov)

        # Start rendering at the sector which contains the player
        stack = Stack([Portal(player.sector, 0, viewWidth - 1)])

        while len(stack) != 0:
            # The original portal contains the whole screen, every subsequent portal is a smaller portion of the screen
            portal: Portal = stack.peek()
            stack.pop()

            # Do not render the sector if it has already been drawn
            if rendered_sectors[portal.sector_id]:
                continue

            rendered_sectors[portal.sector_id] = True
            sector = sectors[portal.sector_id]

            # Loop over every wall within the sector
            for i in range(sector.num_walls):
                # Get the position of the wall within the sector
                wall_start: Wall = walls[sector.start_wall + i]

                # Make sure the second point is not a wall form the next sector
                n = sector.start_wall + i + 1
                if n >= sector.start_wall + sector.num_walls:
                    n = sector.start_wall
                
                wall_end: Wall = walls[n] 

                # Do not render the backside of a portal
                if wall_start.next_sector == player.sector:
                    continue

                # Transform the wall points to be rotated around and relative to the player
                transformed_start_wall = transform(wall_start, player, player.angle)
                transformed_end_wall = transform(wall_end, player, player.angle)

                # Both wall points are behind the player, do not render the wall
                if transformed_start_wall.y <= 0 and transformed_end_wall.y <= 0:
                    continue

                # Get the angle between the wall points and the y axis
                wall_start_angle = normalise_angle(math.atan2(transformed_start_wall.y, transformed_start_wall.x) - math.pi / 2)
                wall_end_angle = normalise_angle(math.atan2(transformed_end_wall.y, transformed_end_wall.x) - math.pi / 2)

                # If the wall is partially in front of the player, clip it against the view frustum
                if transformed_start_wall.y < SETTINGS["znear"] \
                    or transformed_end_wall.y < SETTINGS["znear"] \
                    or wall_start_angle > (hfov / 2) \
                    or wall_end_angle < (-hfov / 2): \
                    
                    # Intersect the wall with the frustum and clip it down to be only within the frustum
                    clipped_start_wall = intersect(transformed_start_wall, transformed_end_wall, frustum.near_left, frustum.far_left)
                    clipped_end_wall = intersect(transformed_start_wall, transformed_end_wall, frustum.near_right, frustum.far_right)

                    # The angle between the wall and the y axis needs to be recalculated if the wall were clipped
                    if (clipped_start_wall != None):
                        transformed_start_wall = clipped_start_wall
                        wall_start_angle = normalise_angle(math.atan2(transformed_start_wall.y, transformed_start_wall.x) - math.pi / 2)

                    if (clipped_end_wall != None):
                        transformed_end_wall = clipped_end_wall
                        wall_end_angle = normalise_angle(math.atan2(transformed_end_wall.y, transformed_end_wall.x) - math.pi / 2)
                
                # Wall is facing away from player, apply back-face culling and thus do not render the wall
                if wall_start_angle < wall_end_angle:
                    continue

                # If both wall points are together on one side of the view frustum, do not render the wall
                if (wall_start_angle < (-hfov / 2) and wall_end_angle < (-hfov / 2)) or (wall_start_angle > (hfov / 2) and wall_end_angle > (hfov / 2)):
                    continue

                # Calculate the x positions of the wall on screen
                screen_start_x = screen_angle_to_x(wall_start_angle)
                screen_end_x = screen_angle_to_x(wall_end_angle)

                # Only draw points within the portal
                if screen_start_x > portal.end_x:
                    continue

                if screen_end_x < portal.start_x:
                    continue

                # Get the floor and ceiling of this sector
                sector_floor = sector.floor
                sector_ceiling = sector.ceiling
                
                # Get the floor and ceiling height of the next sector if the wall is a portal
                next_sector_floor = 0
                next_sector_ceiling = 0

                if wall_start.next_sector != -1:
                    next_sector_floor = sectors[wall_start.next_sector].floor
                    next_sector_ceiling = sectors[wall_start.next_sector].ceiling

                # Calculate the y positions of the wall on screen by projecting the points in 3D
                # Avoid division by zero error
                if transformed_start_wall.y != 0:
                    scaled_start_y = vfov * viewHeight / transformed_start_wall.y
                else:
                    scaled_start_y = vfov * viewHeight / 0.000001

                if transformed_end_wall.y != 0:
                    scaled_end_y = vfov * viewHeight / transformed_end_wall.y
                else:
                    scaled_end_y = vfov * viewHeight / 0.000001
                
                # Calculate the y values for the floor and ceiling of the player's sector
                floor_screen_y = screen_height_to_y(scaled_start_y, sector.floor, player), screen_height_to_y(scaled_end_y, sector.floor, player)  
                ceiling_screen_y = screen_height_to_y(scaled_start_y, sector.ceiling, player), screen_height_to_y(scaled_end_y, sector.ceiling, player)

                # Calculate the y values for the floor and ceiling of the next sector
                portal_floor_screen_y = screen_height_to_y(scaled_start_y, next_sector_floor, player), screen_height_to_y(scaled_end_y, next_sector_floor, player)
                portal_ceiling_screen_y = screen_height_to_y(scaled_start_y, next_sector_ceiling, player), screen_height_to_y(scaled_end_y, next_sector_ceiling, player)

                # Loop over the x cordinates and draw a line
                for x in range(clamp(screen_start_x, portal.start_x, portal.end_x), clamp(screen_end_x, portal.start_x, portal.end_x) + 1):
                    # Avoid division by zero error
                    d = (screen_end_x - screen_start_x)
                    if d == 0:
                        d = 0.000001
                    
                    # Calculate the progress on the x
                    x_progress = (x - screen_start_x) / d

                    # Calculate the y for the given x
                    floor_y = clamp(x_progress * (floor_screen_y[1] - floor_screen_y[0]) + floor_screen_y[0], y_bottom[x], y_top[x])
                    ceiling_y = clamp(x_progress * (ceiling_screen_y[1] - ceiling_screen_y[0]) + ceiling_screen_y[0], y_bottom[x], y_top[x])

                    # The image given back to us is reversed on the x axis and y axis, this is beacause of the way cameras 
                    # work and we have to flip the screen back to being the right way up and flipped on the the  axis for it
                    # to be correct. To convert the calculated coordinates the viewing width/height - 1 (as pixels start from
                    # 0) is taken away by the x/y and the pixel is drawn at the resultant point

                    # Draw the ceiling
                    if ceiling_y < y_top[x]:
                        pygame.draw.line(target, pygame.Color("red"), 
                                         (viewWidth - 1 - x, viewHeight - 1 - ceiling_y), 
                                         (viewWidth - 1 - x, viewHeight - 1 - y_top[x]) )

                    # Draw the floor
                    if floor_y > y_bottom[x]:
                        pygame.draw.line(target, pygame.Color("green"), 
                                         (viewWidth - 1 - x, viewHeight - 1 - y_bottom[x]), 
                                         (viewWidth - 1 - x, viewHeight - 1 - floor_y))

                    # If this wall is a portal, draw the top and bottom wall
                    if wall_start.next_sector != -1:
                        # Calculate the y for the given x for the next sector
                        portal_floor_y = clamp(x_progress * (portal_floor_screen_y[1] - portal_floor_screen_y[0]) + portal_floor_screen_y[0], y_bottom[x], y_top[x])
                        portal_ceiling_y = clamp(x_progress * (portal_ceiling_screen_y[1] - portal_ceiling_screen_y[0]) + portal_ceiling_screen_y[0], y_bottom[x], y_top[x])

                        # If this sector's ceiling is higher than the next sector's ceiling, draw the upper wall
                        if sector_ceiling > next_sector_ceiling:
                            pygame.draw.line(target, pygame.Color("pink"), 
                                             (viewWidth - 1 - x, viewHeight - 1 - portal_ceiling_y), 
                                             (viewWidth - 1 - x, viewHeight - 1 - ceiling_y) )

                        # If this sector's floor is lower than the next sector's floor, draw the lower wall
                        if sector_floor < next_sector_floor:
                            pygame.draw.line(target, pygame.Color("yellow"), 
                                             (viewWidth - 1 - x, viewHeight - 1 - floor_y), 
                                             (viewWidth - 1 - x, viewHeight - 1 - portal_floor_y))

                        # We need to set the portal dimensions so that in the next loop only walls within that new area are considered
                        y_top[x] = clamp(min(min(ceiling_y, portal_ceiling_y), y_top[x]), 0, viewHeight - 1)
                        y_bottom[x] = clamp(max(max(floor_y, portal_floor_y), y_bottom[x]), 0, viewHeight - 1)
                    else:
                        # Draw the wall
                        pygame.draw.line(target, pygame.Color("blue"), 
                                         (viewWidth - 1 - x, viewHeight - 1 - floor_y), 
                                         (viewWidth - 1 - x, viewHeight - 1 - ceiling_y))

                # Push the next sector to be rendered onto the stack
                if wall_start.next_sector != -1:
                    stack.push(Portal(wall_start.next_sector, clamp(screen_start_x, portal.start_x, portal.end_x), clamp(screen_end_x, portal.start_x, portal.end_x)))

        #endregion

        # pygame.draw.line(target, pygame.Color("red"), (player.position.x * 10, player.position.y * 10), (int(math.cos(player.angle) * 5 + player.position.x * 10), int(math.sin(player.angle) * 5 + player.position.y * 10)))
        # target.set_at((int(player.position.x * 10), int(player.position.y * 10)), pygame.Color("green"))

        # for sector in sectors:
        #     for i in range(sector.num_walls):
        #         p1 = walls[sector.start_wall + i]

        #         n = sector.start_wall + i + 1
        #         if n >= sector.start_wall + sector.num_walls:
        #             n = sector.start_wall
                
        #         p2 = walls[n] 

        #         if p1.next_sector == -1:
        #             colour = pygame.Color("black")
        #         else:
        #             colour = pygame.Color("red")
                
        #         pygame.draw.line(target, colour, (p1.position.x*10, p1.position.y*10), (p2.position.x*10, p2.position.y*10))
                
        ''' 
        OBJECTIVE 2: Allow for a scalable window
        '''

        #region Render target resizing

        window_width, window_height = graphics.get_size()
        scale = min(window_width / viewWidth, window_height / viewHeight)

        bar_width = int((window_width - int(viewWidth * scale)) / 2)
        bar_height = int((window_height - int(viewHeight * scale)) / 2)

        '''
        OBJECTIVE 2.1: Resize all content within window to correct size 
        '''

        if SETTINGS["letterbox"]:
            # Adds black bars to either side of the screen
            resized = pygame.transform.scale(target, (int(viewWidth * scale), int(viewHeight * scale)))
            graphics.blit(resized, (bar_width, bar_height))
        else:
            # Stretches image to fill the whole screen
            resized = pygame.transform.scale(target, (window_width, window_height))
            graphics.blit(resized, (0, 0))

        #endregion
        
        pygame.display.update()

        # Cap the framerate at 60 frames per second
        clock.tick(SETTINGS["framerate"])
        pygame.display.set_caption("PLOOM, FPS: {}".format(clock.get_fps()))
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()