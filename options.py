# PLOOM, 0.3 WIP
# Developed by Zain Akram

import math
import pygame, pygame.draw

from settings import SETTINGS
from utility import clamp

NONE = pygame.Rect(0, 0, 9, 9)
HOVER = pygame.Rect(9, 0, 9, 9)

class Options():
    def __init__(self, font, textures, target, application):
        self.__target = target
        self.__textures = textures
        self.__application = application
        self.__font = font
        self.__state = lambda mouse_pos: self.menu(mouse_pos)

        self.__current_mouse = pygame.mouse.get_pressed()
        self.__previous_mouse = self.__current_mouse

        self.__cursor = False
        self.__track_slider = False

    def render(self):
        self.__current_mouse = pygame.mouse.get_pressed()
        self.__cursor = False

        # Mouse left-click released
        if not(self.__current_mouse[0]) and self.__previous_mouse[0]:
            self.__track_slider = False

        viewWidth = SETTINGS["viewWidth"]
        viewHeight = SETTINGS["viewHeight"]

        window_width, window_height = pygame.display.get_surface().get_size()
        scale = min(window_width / viewWidth, window_height / viewHeight)

        bar_width = int((window_width - int(viewWidth * scale)) / 2)
        bar_height = int((window_height - int(viewHeight * scale)) / 2)

        mouse_pos = (int((pygame.mouse.get_pos()[0] - bar_width) / scale), int((pygame.mouse.get_pos()[1] - bar_height) / scale))

        if self.__state != None:
            self.__state(mouse_pos)
        
        #region Draw cursor
        
        if self.__cursor:
            sprite = self.__textures.subsurface(HOVER)
        else:
            sprite = self.__textures.subsurface(NONE)
        self.__target.blit(sprite, (mouse_pos[0] - 4, mouse_pos[1] - 4))

        #endregion
        
        self.__previous_mouse = self.__current_mouse

    def text_handler(self, mouse_pos, texts, states, rect, property = "", percentage = True):
        colour = pygame.Color("#A663CC")

        # Draw outline
        pygame.draw.rect(self.__target, pygame.Color("#A663CC"), pygame.Rect(rect.x - 2, rect.y - 1, rect.width + 4, rect.height * len(texts) + 3), 1)

        # Draw each text
        for i, text in enumerate(texts):
            
            if text == "BOOL":
                value = SETTINGS[property]

                if rect.collidepoint(mouse_pos):
                    colour = pygame.Color("#B298DC")
                    self.__cursor = True
                    # Mouse left-click pressed
                    if self.__current_mouse[0] and not(self.__previous_mouse[0]):
                        SETTINGS[property] = not(SETTINGS[property])
                self.__font.render(self.__target, str(value).upper(), pygame.Vector2(rect.x, rect.y), colour)

            elif text == "SLIDER": 
                value = SETTINGS[property]

                if percentage: 
                    denominator = 2
                    percent = value
                    print(percent)
                else:
                    denominator = 1
                    lower_bound = SETTINGS[property + "LowerBound"]
                    upper_bound = SETTINGS[property + "UpperBound"] - lower_bound
                    percent = (math.degrees(value) - lower_bound) / upper_bound
                    print(math.degrees(value))

                slider_bar = pygame.Rect(rect.x + 32, rect.y + 3, 63, 3)
                slider_rect = pygame.Rect(rect.x + int(60 / denominator * percent) + 32, rect.y + 1, 3, 7)
                slider_hitbox = pygame.Rect(rect.x + 32, rect.y + 1, 63, 7)

                if slider_hitbox.collidepoint(mouse_pos):
                    colour = pygame.Color("#B298DC")
                    self.__cursor = True
                    # Mouse left-click pressed
                    if self.__current_mouse[0] and not(self.__previous_mouse[0]):
                        self.__track_slider = True

                if self.__track_slider:
                    slider_rect.x = clamp(mouse_pos[0] - 1, rect.x + 32, rect.x + 32 + 60)
                    colour = pygame.Color("#B298DC")
                    self.__cursor = True
                    percent = (slider_rect.x - rect.x - 32) / (60 / denominator)
                    if percentage:
                        SETTINGS[property] = percent
                    else:
                        SETTINGS[property] = math.radians(percent * upper_bound + lower_bound)

                pygame.draw.rect(self.__target, pygame.Color("#A663CC"), slider_bar)
                pygame.draw.rect(self.__target, colour, slider_rect)

                if percentage:
                    number = str(round(percent * 100)) + "%"
                else:
                    number = str(round(percent * upper_bound + lower_bound)) + "°"
                self.__font.render(self.__target, number, pygame.Vector2(rect.x, rect.y), colour)
            
            else:                
                if rect.collidepoint(mouse_pos):
                    colour = pygame.Color("#B298DC")
                    self.__cursor = True
                    # Mouse left-click pressed
                    if self.__current_mouse[0] and not(self.__previous_mouse[0]):
                        self.__state = states[i]
                else:
                    colour = pygame.Color("#A663CC")
                self.__font.render(self.__target, text, pygame.Vector2(rect.x, rect.y), colour)
            rect.y += 8

    def menu(self, mouse_pos):
        texts = ["START", "OPTIONS", "ABOUT", "EXIT"]

        states = [lambda mouse_pos: self.start(mouse_pos), 
                  lambda mouse_pos: self.options(mouse_pos), 
                  lambda mouse_pos: self.about(mouse_pos),
                  lambda mouse_pos: self.exit(mouse_pos)]
        
        rect = pygame.Rect(132, 96, 55, 8)

        self.text_handler(mouse_pos, texts, states, rect)

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 100), (128, 100))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 100), (319 - 128, 100))
        
    def start(self, mouse_pos):
        self.__application.load_level("content/map.json")
    
    def options(self, mouse_pos):
        texts = ["SENSITIVITY", "HFOV", "VFOV", "PLAYER SPEED", "LETTERBOX", "MENU SPIN", "BACK"]
        
        states = [lambda mouse_pos: self.sensitivity(mouse_pos), 
                  lambda mouse_pos: self.hfov(mouse_pos), 
                  lambda mouse_pos: self.vfov(mouse_pos),
                  lambda mouse_pos: self.player_speed(mouse_pos),
                  lambda mouse_pos: self.letterbox(mouse_pos),
                  lambda mouse_pos: self.menu_spin(mouse_pos),
                  lambda mouse_pos: self.menu(mouse_pos)]

        rect = pygame.Rect(112, 95, 95, 8)

        # Draw the title        
        self.__font.render(self.__target, "OPTIONS", pygame.Vector2(132, 85), pygame.Color("#A663CC"))

        self.text_handler(mouse_pos, texts, states, rect)

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 90), (130, 90))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 90), (319 - 130, 90))

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 100), (108, 100))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 100), (319 - 108, 100))
        
    def about(self, mouse_pos):
        pass

    def exit(self, mouse_pos):
        self.__application.is_running = False

    def sensitivity(self, mouse_pos):
        texts = ["SLIDER", "BACK"]
        
        states = [lambda mouse_pos: None, 
                  lambda mouse_pos: self.options(mouse_pos)]    
            
        rect = pygame.Rect(112, 95, 95, 8)
        
        # Draw the title        
        self.__font.render(self.__target, "SENSITIVTY", pygame.Vector2(120, 85), pygame.Color("#A663CC"))
        
        self.text_handler(mouse_pos, texts, states, rect, "sensitivityMultiplier", True)

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 90), (118, 90))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 90), (319 - 118, 90))

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 100), (108, 100))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 100), (319 - 108, 100))
        
    def hfov(self, mouse_pos):
        texts = ["SLIDER", "BACK"]

        states = [lambda mouse_pos: None, 
                  lambda mouse_pos: self.options(mouse_pos)]    
            
        rect = pygame.Rect(112, 95, 95, 8)
        
        # Draw the title        
        self.__font.render(self.__target, "HFOV", pygame.Vector2(144, 85), pygame.Color("#A663CC"))

        self.text_handler(mouse_pos, texts, states, rect, "hfov", False)

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 90), (142, 90))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 90), (319 - 142, 90))

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 100), (108, 100))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 100), (319 - 108, 100))

    def vfov(self, mouse_pos):
        texts = ["SLIDER", "BACK"]

        states = [lambda mouse_pos: None, 
                  lambda mouse_pos: self.options(mouse_pos)]            
        
        rect = pygame.Rect(112, 95, 95, 8)
        
        # Draw the title
        self.__font.render(self.__target, "VFOV", pygame.Vector2(144, 85), pygame.Color("#A663CC"))
        
        self.text_handler(mouse_pos, texts, states, rect, "vfov", False)

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 90), (142, 90))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 90), (319 - 142, 90))

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 100), (108, 100))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 100), (319 - 108, 100))
        
    def player_speed(self, mouse_pos):
        texts = ["SLIDER", "BACK"]

        states = [lambda mouse_pos: None, 
                  lambda mouse_pos: self.options(mouse_pos)]           
        
        rect = pygame.Rect(112, 95, 95, 8)
        
        # Draw the title        
        self.__font.render(self.__target, "PLAYER SPEED", pygame.Vector2(112, 85), pygame.Color("#A663CC"))

        self.text_handler(mouse_pos, texts, states, rect, "playerSpeedMultiplier", True)

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 90), (110, 90))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 90), (319 - 110, 90))

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 100), (108, 100))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 100), (319 - 108, 100))

    def letterbox(self, mouse_pos):
        texts = ["BOOL", "BACK"]

        states = [lambda mouse_pos: None, 
                  lambda mouse_pos: self.options(mouse_pos)]   
        
        rect = pygame.Rect(140, 95, 39, 8)

        # Draw the title        
        self.__font.render(self.__target, "LETTERBOX", pygame.Vector2(124, 85), pygame.Color("#A663CC"))

        self.text_handler(mouse_pos, texts, states, rect, "letterbox")

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 90), (122, 90))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 90), (319 - 122, 90))

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 100), (136, 100))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 100), (319 - 136, 100))

    def menu_spin(self, mouse_pos):
        texts = ["BOOL", "BACK"]

        states = [lambda mouse_pos: None, 
                  lambda mouse_pos: self.options(mouse_pos)]    
            
        rect = pygame.Rect(140, 95, 39, 8)

        # Draw the title        
        self.__font.render(self.__target, "MENU SPIN", pygame.Vector2(124, 85), pygame.Color("#A663CC"))

        self.text_handler(mouse_pos, texts, states, rect, "menuSpin")
        
        pygame.draw.line(self.__target, pygame.Color("red"), (0, 90), (122, 90))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 90), (319 - 122, 90))

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 100), (136, 100))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 100), (319 - 136, 100))