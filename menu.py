# PLOOM, 0.3 WIP
# Developed by Zain Akram

import pygame, pygame.draw

from engine import Scene
from font import Font
from options import Options
from settings import SETTINGS

TEXT = pygame.Rect(0, 9, 312, 9)
BACKGROUND = pygame.Rect(0, 0, 320, 180)

class Menu(Scene):
    def __init__(self, application):
        super().__init__(application)
        self.target = pygame.Surface((SETTINGS["viewWidth"], SETTINGS["viewHeight"]))        
        pygame.mouse.set_visible(False)

        self.__current_image = pygame.Surface((BACKGROUND.width, BACKGROUND.height))
        self.__frame = 0
        self.__frame_length = float(1 / 24)
        self.__time_remaining = float(self.__frame_length)

        # Objects
        self.__font = None
        self.__textures = None
        self.__background = None
        self.__options = None

    def load_content(self):
        pygame.event.set_grab(False)
        self.__textures = pygame.image.load("content/textures.png").convert_alpha()
        self.__background: pygame.Surface = pygame.image.load("content/background.png").convert_alpha()
        self.__font = Font(self.__textures.subsurface(TEXT))
        self.__options = Options(self.__font, self.__textures, self.target, self.application)

    def update(self, delta_time):
        if SETTINGS["menuSpin"]:
            if self.__time_remaining > 0:
                self.__time_remaining -= delta_time
            else:
                self.__frame += 1
                self.__time_remaining = float(self.__frame_length)

            if self.__frame >= 29:
                self.__frame = 0
        else:
            self.__frame = 0

        self.__current_image = self.__background.subsurface(BACKGROUND.x, BACKGROUND.y + self.__frame * BACKGROUND.height, BACKGROUND.width, BACKGROUND.height)

        super().update(delta_time)
    
    def render(self):
        self.target.fill(SETTINGS["menuColour"])

        self.target.blit(self.__current_image, (0, -40))

        self.__options.render()
        
        super().render()