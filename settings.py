# PLOOM, 0.3 WIP
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