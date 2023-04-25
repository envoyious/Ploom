# PLOOM, 1.0 FINAL
# Developed by Zain Akram

import math
import pygame

# Clamp the value to the inclusive range of min and max
def clamp(value, min_value, max_value):
        return min(max(value, min_value), max_value)

# Translates point a to be relative player
def translate(point, player):
    return pygame.Vector2(point.position.x - player.get_position().x, point.position.y - player.get_position().y)

# Rotate a point given an angle
def rotate(point, angle):
    return pygame.Vector2(point.x * math.sin(angle) - point.y * math.cos(angle), point.x * math.cos(angle) + point.y * math.sin(angle))

# Transforms position from world space into viewport space
def transform(point, player, angle):
    point = translate(point, player)
    return rotate(point, angle)

# Normalises angle to between -pi and pi
def normalise_angle(angle):
    return angle - (2 * math.pi) * math.floor((angle + math.pi) / (2 * math.pi))

# Calculates intersection point given two segments, returns (None) if no intersection
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

# Convert angle in (-HFOV / 2) to (HFOV / 2) into a x coordinate

# This changes how each angle withing the FOV is seen. The fish eye view calculation is correct to life 
# as it takes into consideration the curvature of the eyeball so the angle directly infront of the camera 
# is shorter than the edges of the wall to the left and right. Linear view calculates the progression 
# from the first point to the second linearly and does not consider the distance from the camera. Corrected
# view dicreases distortion by using the perpendicular distance of the point from the camera so that flat 
# walls do not change in size when moving and rotating

def screen_angle_to_x(angle, hfov, view_width, view_mode):
    if view_mode == 0:
        # Linear view
        return int((view_width / 2) - angle / (hfov / 2) * view_width / 2)
    elif view_mode == 1:
        # Fish eye view
        return int(-(view_width / 2) / math.sin(hfov / 2) * math.sin(angle) + view_width / 2)
    else:
        # Corrected view
        return int((-math.tan(math.pi * angle / (2 * hfov)) + 1) * view_width / 2)

# Convert ceiling and floor heights into a y coordinate
def screen_height_to_y(scaled_y, plane_height, player_z, transformed_y, view_height, yaw):
    return int(view_height / 2 + (y_shear(plane_height, transformed_y, yaw) - player_z) * scaled_y)

# Apply y-shearing by shifting pixels up or down
def y_shear(plane_height, y, yaw):
    return plane_height - y * yaw

# Shade walls based on the distance of the pixel from the player
def shade_per_pixel(colour, x, screen_start_x, screen_end_x, start, end):
    d = (screen_end_x - screen_start_x)
    if d == 0:
        d = 0.000001
    distance = ((x - screen_start_x) * (end.y - start.y) / d + start.y) * 15

    return (clamp(colour.r - distance, 0, colour.r), 
            clamp(colour.g - distance, 0, colour.g),
            clamp(colour.b - distance, 0, colour.b))

# Shade walls based on the angle of the wall
def shade_by_angle(colour, start: pygame.Vector2, end):
    angle  = math.degrees(math.atan2(start.y - end.y, start.x - end.x))

    if angle <= 0:
        distance = angle / 360 * 80
    else:
        distance = -(angle / 360 * 80)

    return (clamp(colour.r - distance, 0, 255), 
            clamp(colour.g - distance, 0, 255),
            clamp(colour.b - distance, 0, 255))

# Shade the wall/floor/ceiling based on the distance from the player
def shade_per_wall(colour, point, start, end):
    average = (start + end) / 2
    distance = average.distance_to((point)) * 15
    return (clamp(colour.r - distance, 0, colour.r), 
            clamp(colour.g - distance, 0, colour.g),
            clamp(colour.b - distance, 0, colour.b))

# Shade floor/ceiling by height
def shade_by_height(colour, height):
    distance = height * 15
    return (clamp(colour.r - distance, 0, 255), 
            clamp(colour.g - distance, 0, 255),
            clamp(colour.b - distance, 0, 255))

# -1 right, 1 left given a point and a line
def point_side(point, line_start, line_end):
    return math.copysign(1, (line_end.x - line_start.x) * (point.y - line_start.y) - (line_end.y - line_start.y) * (point.x - line_start.x))

# Point is in sector if it is on the left side of all walls
def point_in_sector(point, sector, walls):
    for i in range(sector.num_walls):
        wall_start = walls[sector.start_wall + i]

        # Make sure the sector does not contain any walls from a different sector
        n = sector.start_wall + i + 1
        if n >= sector.start_wall + sector.num_walls:
            n = sector.start_wall
        
        wall_end = walls[n] 

        if point_side(point, wall_start.position, wall_end.position) > 0:
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