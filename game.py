# PLOOM, 1.0 FINAL
# Developed by Zain Akram

import math
import pygame, pygame.draw
import json

from engine import Scene
from font import Font
from options import Options
from settings import SETTINGS
from utility import *

TEXT = pygame.Rect(0, 9, 328, 9)

class Frustum:
    def __init__(self, angle, znear, zfar):
        left = rotate(pygame.Vector2(0, 1), math.pi / 2 - (angle / 2))
        right = rotate(pygame.Vector2(0, 1), math.pi / 2 - (-angle / 2))

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
    def __init__(self, position, angle, yaw):
        self.__position = position
        self.__angle = math.radians(angle)
        self.__yaw = yaw
        self.__sector = 0

        self.__yaw_bounds = SETTINGS["yawBounds"]
        self.__previous_key = pygame.key.get_pressed()

    def get_position(self):
        return self.__position
    
    def get_angle(self):
        return self.__angle
    
    def get_yaw(self):
        return self.__yaw
    
    def get_sector(self):
        return self.__sector

    def update(self, delta_time, floor_height):
        mouse_x, mouse_y  = pygame.mouse.get_rel()
        keys_down = pygame.key.get_pressed()

        sensitivity = SETTINGS["baseSensitivity"] * SETTINGS["sensitivityMultiplier"]
        sensitivity_multiplier = SETTINGS["keyboardSensitivityMultiplier"]
        player_speed = SETTINGS["basePlayerSpeed"] * SETTINGS["playerSpeedMultiplier"]

        # Activate/Deactivate mouse input
        if keys_down[pygame.K_ESCAPE] and not(self.__previous_key[pygame.K_ESCAPE]):
            #pygame.mouse.set_visible(not(pygame.mouse.get_visible()))
            pygame.event.set_grab(not(pygame.event.get_grab()))

        # Mouse rotation
        if (pygame.event.get_grab()):
            self.__angle += mouse_x * sensitivity
            self.__yaw = clamp(self.__yaw - mouse_y * sensitivity * 3.8, -self.__yaw_bounds, self.__yaw_bounds)

        # Left and right rotation
        if (keys_down[pygame.K_LEFT]):
            self.__angle -= sensitivity * sensitivity_multiplier * delta_time
        if (keys_down[pygame.K_RIGHT]):
            self.__angle += sensitivity * sensitivity_multiplier * delta_time

        # Up and down rotaion
        if (keys_down[pygame.K_UP]):
            self.__yaw = clamp(self.__yaw + sensitivity * 3.8 * sensitivity_multiplier * delta_time, -self.__yaw_bounds, self.__yaw_bounds)
        if (keys_down[pygame.K_DOWN]):
            self.__yaw = clamp(self.__yaw - sensitivity * 3.8 * sensitivity_multiplier * delta_time, -self.__yaw_bounds, self.__yaw_bounds)

        # Backwards and forwards movement
        if (keys_down[pygame.K_w]):
            self.__position.x += math.cos(self.__angle) * player_speed * delta_time
            self.__position.y += math.sin(self.__angle) * player_speed * delta_time
        
        if (keys_down[pygame.K_s]):
            self.__position.x -= math.cos(self.__angle) * player_speed * delta_time
            self.__position.y -= math.sin(self.__angle) * player_speed * delta_time

        # Strafe left and right
        if (keys_down[pygame.K_a]):
            self.__position.x += math.sin(self.__angle) * player_speed * delta_time
            self.__position.y -= math.cos(self.__angle) * player_speed * delta_time
        
        if (keys_down[pygame.K_d]):
            self.__position.x -= math.sin(self.__angle) * player_speed * delta_time
            self.__position.y += math.cos(self.__angle) * player_speed * delta_time

        self.__position.z = floor_height + SETTINGS["playerHeight"]

        self.__previous_key = keys_down

    def find_sector(self, sectors, walls):
        # Breath Fisrst Traversal is used as player is likely to be in neighbouring sectors
        queue = Queue([])
        visited = list([])

        visited.append(self.__sector)
        queue.enqueue(self.__sector)
        found = None

        while len(queue) != 0:
            id = queue.peek()
            queue.dequeue()
            sector = sectors[id]

            if point_in_sector(self.__position, sector, walls):
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
            self.__sector = 0
        else:
            self.__sector = found

class Game(Scene):
    def __init__(self, application, path):
        super().__init__(application)
        self._target = pygame.Surface((SETTINGS["viewWidth"], SETTINGS["viewHeight"]))

        # Create objects
        self.__sectors, self.walls, self.num_sectors, player_pos = self.__load_map(path)
        self.__player = Player(pygame.Vector3(player_pos.x, player_pos.y, 0), 0, 0)
        self.__player_height = SETTINGS["playerHeight"]
        self.__font = None
        self.__options = None

        # Create transparent darken layer for menu
        menu_colour = pygame.Color(SETTINGS["menuColour"])
        self.__darken = pygame.Surface((SETTINGS["viewWidth"], SETTINGS["viewHeight"]), pygame.SRCALPHA)
        self.__darken.fill((menu_colour.r, menu_colour.g, menu_colour.b, 160))

    def __load_map(self, path):
        sectors = []
        walls = []

        with open(path) as file:
            data = json.load(file)

        for i, n in enumerate(data["sectors"]):
            sector = Sector(i, n["startWall"], n["numWalls"], n["floor"], n["ceiling"])
            sectors.append(sector)

        for i, n in enumerate(data["walls"]):
            wall = Wall(pygame.Vector2(n["x"], n["y"]), n["nextSector"])
            walls.append(wall)

        num_sectors = len(data["sectors"])

        player_pos = pygame.Vector2(data["player"]["x"], data["player"]["y"])

        return sectors, walls, num_sectors, player_pos

    def load_content(self):
        pygame.event.set_grab(True)
        self.textures = pygame.image.load("content/textures.png").convert_alpha()
        self.__font = Font(self.textures.subsurface(TEXT))
        self.__options = Options(self.__font, self.textures, self._application)
        # super().load_content()

    def update(self, delta_time):
        # Update the player
        floor_height = self.__sectors[self.__player.get_sector()].floor
        self.__player.update(delta_time, floor_height)
        self.__player.find_sector(self.__sectors, self.walls)

        super().update(delta_time)

    def render(self):
        self._target.fill(SETTINGS["clearColour"])
        
        view_width = SETTINGS["viewWidth"]
        view_height = SETTINGS["viewHeight"]

        if SETTINGS["linearViewMode"]:
            view_mode = 0
        elif SETTINGS["fishEyeViewMode"]:
            view_mode = 1
        elif SETTINGS["correctedViewMode"]:
            view_mode = 2

        if SETTINGS["pixelLightMode"]:
            light_mode = 0
        elif SETTINGS["angleLightMode"]:
            light_mode = 1
        elif SETTINGS["sectorLightMode"]:
            light_mode = 2

        hfov = SETTINGS["hfov"]
        vfov = SETTINGS["vfov"]
        znear = SETTINGS["znear"]
        zfar = SETTINGS["zfar"]
        
        #region Render walls

        # Keep track of whether or not a sector has been drawn
        #rendered_sectors = [False for i in range(self.num_sectors)]

        # Keep track of where on the screen a portal is for each x value
        y_bottom = [0 for i in range(view_width)]
        y_top = [view_width - 1 for i in range(view_width)]
        
        # Create the view frustum
        frustum = Frustum(hfov, znear, zfar)

        # Start rendering at the sector which contains the player
        stack = Stack([Portal(self.__player.get_sector(), 0, view_width - 1)])

        while len(stack) != 0:
            # The original portal contains the whole screen, every subsequent portal is a smaller portion of the screen
            portal: Portal = stack.peek()
            stack.pop()

            # Do not render the sector if it has already been drawn
            #if rendered_sectors[portal.sector_id]:
            #    continue

            #rendered_sectors[portal.sector_id] = True
            sector = self.__sectors[portal.sector_id]

            # Loop over every wall within the sector
            for i in range(sector.num_walls):
                # Get the position of the wall within the sector
                wall_start: Wall = self.walls[sector.start_wall + i]

                # Make sure the second point is not a wall form the next sector
                n = sector.start_wall + i + 1
                if n >= sector.start_wall + sector.num_walls:
                    n = sector.start_wall
                
                wall_end: Wall = self.walls[n] 

                # Do not render the backside of a portal
                if wall_start.next_sector == self.__player.get_sector():
                    continue

                # Transform the wall points to be rotated around and relative to the player
                transformed_start_wall = transform(wall_start, self.__player, self.__player.get_angle())
                transformed_end_wall = transform(wall_end, self.__player, self.__player.get_angle())

                # Both wall points are behind the player, do not render the wall
                if transformed_start_wall.y <= 0 and transformed_end_wall.y <= 0:
                    continue

                # Get the angle between the wall points and the y axis
                wall_start_angle = normalise_angle(math.atan2(transformed_start_wall.y, transformed_start_wall.x) - math.pi / 2)
                wall_end_angle = normalise_angle(math.atan2(transformed_end_wall.y, transformed_end_wall.x) - math.pi / 2)

                # If the wall is partially in front of the player, clip it against the view frustum
                if transformed_start_wall.y < znear \
                    or transformed_end_wall.y < znear \
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
                screen_start_x = screen_angle_to_x(wall_start_angle, hfov, view_width, view_mode)
                screen_end_x = screen_angle_to_x(wall_end_angle, hfov, view_width, view_mode)

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
                    next_sector_floor = self.__sectors[wall_start.next_sector].floor
                    next_sector_ceiling = self.__sectors[wall_start.next_sector].ceiling

                # Calculate the y positions of the wall on screen by projecting the points in 3D
                # Avoid division by zero error
                if transformed_start_wall.y != 0:
                    scaled_start_y = vfov * view_height / transformed_start_wall.y
                else:
                    scaled_start_y = vfov * view_height / 0.000001

                if transformed_end_wall.y != 0:
                    scaled_end_y = vfov * view_height / transformed_end_wall.y
                else:
                    scaled_end_y = vfov * view_height / 0.000001

                player_z = self.__player.get_position().z 
                
                # Calculate the y values for the floor and ceiling of the player's sector
                floor_screen_y = screen_height_to_y(scaled_start_y, sector_floor, player_z, transformed_start_wall.y, view_height, self.__player.get_yaw()), \
                                 screen_height_to_y(scaled_end_y, sector_floor, player_z, transformed_end_wall.y, view_height, self.__player.get_yaw())  
                
                ceiling_screen_y = screen_height_to_y(scaled_start_y, sector_ceiling, player_z, transformed_start_wall.y, view_height, self.__player.get_yaw()), \
                                   screen_height_to_y(scaled_end_y, sector_ceiling, player_z, transformed_end_wall.y, view_height, self.__player.get_yaw())

                # Calculate the y values for the floor and ceiling of the next sector
                portal_floor_screen_y = screen_height_to_y(scaled_start_y, next_sector_floor, player_z, transformed_start_wall.y, view_height, self.__player.get_yaw()), \
                                        screen_height_to_y(scaled_end_y, next_sector_floor, player_z, transformed_end_wall.y, view_height, self.__player.get_yaw())
                
                portal_ceiling_screen_y = screen_height_to_y(scaled_start_y, next_sector_ceiling, player_z, transformed_start_wall.y, view_height, self.__player.get_yaw()), \
                                          screen_height_to_y(scaled_end_y, next_sector_ceiling, player_z, transformed_end_wall.y, view_height, self.__player.get_yaw())

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

                    # The image given back to us is reversed on the x axis and y axis, this is because of the way cameras 
                    # work and we have to flip the screen back to being the right way up and flipped on the y axis for it
                    # to be correct. To convert the calculated coordinates the viewing width/height - 1 (as pixels start from
                    # 0) is taken away by the x/y and the pixel is drawn at the resultant point

                    sector_start = self.walls[sector.start_wall].position
                    sector_end = self.walls[int(sector.start_wall + sector.num_walls / 2)].position

                    # Draw the ceiling
                    if ceiling_y < y_top[x]:

                        if light_mode == 0:
                            colour = shade_per_wall(pygame.Color("#98B8DC"), (self.__player.get_position().x, self.__player.get_position().y), sector_start, sector_end)
                        elif light_mode == 1:
                            colour = shade_by_height(pygame.Color("#98B8DC"), -sector.ceiling + self.__player_height + 5)
                        else:
                            colour = shade_per_wall(pygame.Color("#98B8DC"), (self.__player.get_position().x, self.__player.get_position().y), sector_start, sector_end)

                        pygame.draw.line(self._target, colour, 
                                         (view_width - 1 - x, view_height - 1 - ceiling_y), 
                                         (view_width - 1 - x, view_height - 1 - y_top[x]) )
                        #self.target.set_at((int(view_width - 1 - x), int(view_height - 1 - y_top[x])), pygame.Color("#FF0000"))

                    # Draw the floor
                    if floor_y > y_bottom[x]:

                        if light_mode == 0:
                            colour = shade_per_wall(pygame.Color("#A663CC"), (self.__player.get_position().x, self.__player.get_position().y), sector_start, sector_end)
                        elif light_mode == 1:
                            colour = shade_by_height(pygame.Color("#A663CC"), sector.floor - self.__player_height)
                        else:
                            colour = shade_per_wall(pygame.Color("#A663CC"), (self.__player.get_position().x, self.__player.get_position().y), sector_start, sector_end)

                        pygame.draw.line(self._target, colour, 
                                         (view_width - 1 - x, view_height - 1 - y_bottom[x]), 
                                         (view_width - 1 - x, view_height - 1 - floor_y))
                        #self.target.set_at((int(view_width - 1 - x), int(view_height - 1 - y_bottom[x])), pygame.Color("#FF0000"))

                    # If this wall is a portal, draw the top and bottom wall
                    if wall_start.next_sector != -1:
                        # Calculate the y for the given x for the next sector
                        portal_floor_y = clamp(x_progress * (portal_floor_screen_y[1] - portal_floor_screen_y[0]) + portal_floor_screen_y[0], y_bottom[x], y_top[x])
                        portal_ceiling_y = clamp(x_progress * (portal_ceiling_screen_y[1] - portal_ceiling_screen_y[0]) + portal_ceiling_screen_y[0], y_bottom[x], y_top[x])

                        # If this sector's ceiling is higher than the next sector's ceiling, draw the upper wall
                        if sector_ceiling > next_sector_ceiling:
                            if light_mode == 0:
                                colour = shade_per_pixel(pygame.Color("#B8D0EB"), x, screen_start_x, screen_end_x, transformed_start_wall, transformed_end_wall)
                            elif light_mode == 1:
                                colour = shade_by_angle(pygame.Color("#B8D0EB"), wall_start.position, wall_end.position)
                            else:
                                colour = shade_per_wall(pygame.Color("#B8D0EB"), (0, 0), transformed_start_wall, transformed_end_wall)

                            pygame.draw.line(self._target, colour, 
                                             (view_width - 1 - x, view_height - 1 - portal_ceiling_y), 
                                             (view_width - 1 - x, view_height - 1 - ceiling_y) )

                        # If this sector's floor is lower than the next sector's floor, draw the lower wall
                        if sector_floor < next_sector_floor:
                            if light_mode == 0:
                                colour = shade_per_pixel(pygame.Color("#B298DC"), x, screen_start_x, screen_end_x, transformed_start_wall, transformed_end_wall)
                            elif light_mode == 1:
                                colour = shade_by_angle(pygame.Color("#B298DC"), wall_start.position, wall_end.position)
                            else:
                                colour = shade_per_wall(pygame.Color("#B298DC"), (0, 0), transformed_start_wall, transformed_end_wall)

                            pygame.draw.line(self._target, colour, 
                                             (view_width - 1 - x, view_height - 1 - floor_y), 
                                             (view_width - 1 - x, view_height - 1 - portal_floor_y))

                        # We need to set the portal dimensions so that in the next loop only walls within that new area are considered
                        y_top[x] = clamp(min(min(ceiling_y, portal_ceiling_y), y_top[x]), 0, view_height - 1)
                        y_bottom[x] = clamp(max(max(floor_y, portal_floor_y), y_bottom[x]), 0, view_height - 1)
                    else:
                        # Draw the wall

                        if light_mode == 0:
                            colour = shade_per_pixel(pygame.Color("#6F2DBD"), x, screen_start_x, screen_end_x, transformed_start_wall, transformed_end_wall)
                        elif light_mode == 1:
                            colour = shade_by_angle(pygame.Color("#6F2DBD"), wall_start.position, wall_end.position)
                        else:
                            colour = shade_per_wall(pygame.Color("#6F2DBD"), (0, 0), transformed_start_wall, transformed_end_wall)

                        pygame.draw.line(self._target, colour, 
                                         (view_width - 1 - x, view_height - 1 - floor_y), 
                                         (view_width - 1 - x, view_height - 1 - ceiling_y))

                # Push the next sector to be rendered onto the stack
                if wall_start.next_sector != -1:
                    stack.push(Portal(wall_start.next_sector, clamp(screen_start_x, portal.start_x, portal.end_x), clamp(screen_end_x, portal.start_x, portal.end_x)))

        #endregion

        # Draw the 2D minimap
        scale_factor = 7
        line_length = 36
        offset = hfov / 2

        # Draw the horizontal field of view
        pygame.draw.line(self._target, pygame.Color("red"), 
                         (self.__player.get_position().x * scale_factor, self.__player.get_position().y * scale_factor), 
                         (int(math.cos(-offset + self.__player.get_angle()) * line_length + self.__player.get_position().x * scale_factor), int(math.sin(-offset + self.__player.get_angle()) * line_length + self.__player.get_position().y * scale_factor)))
        
        pygame.draw.line(self._target, pygame.Color("red"), 
                         (self.__player.get_position().x * scale_factor, self.__player.get_position().y * scale_factor), 
                         (int(math.cos(offset + self.__player.get_angle()) * line_length + self.__player.get_position().x * scale_factor), int(math.sin(offset + self.__player.get_angle()) * line_length + self.__player.get_position().y * scale_factor)))

        # Draw the player
        self._target.set_at((int(self.__player.get_position().x * scale_factor), int(self.__player.get_position().y * scale_factor)), pygame.Color("green"))

        # Draw the walls
        for sector in self.__sectors:
            for i in range(sector.num_walls):
                p1 = self.walls[sector.start_wall + i]

                n = sector.start_wall + i + 1
                if n >= sector.start_wall + sector.num_walls:
                    n = sector.start_wall
                
                p2 = self.walls[n] 

                if p1.next_sector == -1:
                    colour = pygame.Color("black")
                else:
                    colour = pygame.Color("red")
                
                pygame.draw.line(self._target, colour, 
                                 (p1.position.x * scale_factor + 1, p1.position.y * scale_factor + 1), 
                                 (p2.position.x * scale_factor + 1, p2.position.y * scale_factor + 1))

        # Menu
        if (not(pygame.event.get_grab())):
            self._target.blit(self.__darken, (0, 0))
            self.__options.render(self._target)

        super().render()