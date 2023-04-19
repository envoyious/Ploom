# PLOOM, 0.3 WIP
# Developed by Zain Akram

import sys, math
import pygame
import json

class Settings:
    def __init__(self, path):
        self.__data = None

        with open(path) as file:
            self.__data: dict = json.load(file)

        # https://stackoverflow.com/questions/1136826/what-does-sys-intern-do-and-when-should-it-be-used
        for key in self.__data.keys():
            sys.intern(key)
        
        colour = pygame.Color(self["clearColour"])
        self["clearColour"] = (colour.r, colour.g, colour.b)
        self["hfov"] = math.radians(self["hfov"])
        self["vfov"] = math.radians(self["vfov"])

    def __getitem__(self, item):
        return self.__data[item]
    
    def __setitem__(self, item, value):
        self.__data[item] = value

SETTINGS = Settings("content/config.json")