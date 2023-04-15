# PLOOM, 0.2 WIP
# Developed by Zain Akram

import math
import pygame
import json

class Settings:
    def __init__(self, path):
        self.__data = None

        with open(path) as file:
            self.__data = json.load(file)
        
        self["clearColour"] = pygame.Color(self["clearColour"])
        self["hfov"] = math.radians(self["hfov"])
        self["vfov"] = math.radians(self["vfov"])

    def __getitem__(self, item):
        return self.__data[item]
    
    def __setitem__(self, item, value):
        self.__data[item] = value

SETTINGS = Settings("content/config.json")

'''
# Screen size
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 360
VIEW_WIDTH = 320
VIEW_HEIGHT = 180

CLEAR_COLOUR = (pygame.Color("cornflower blue"))
LETTERBOX = True

# Engine
FRAMERATE = 60
HFOV = math.radians(103)
VFOV = math.radians(15)
ZNEAR = 0.000001
ZFAR = 100

# Gameplay
PLAYER_HEIGHT = 2.4
SENSITIVITY = 0.00086
SENSITIVITY_MULTIPLIER = 30.25
PLAYER_SPEED = 0.06
'''