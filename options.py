# PLOOM, 1.0 FINAL
# Developed by Zain Akram

import math
import pygame, pygame.draw
import os

from settings import SETTINGS
from utility import clamp

NONE = pygame.Rect(0, 0, 9, 9)
HOVER = pygame.Rect(9, 0, 9, 9)

class Options():
    def __init__(self, font, textures, application):
        self.__unscaled = pygame.Surface((320, 180), flags=pygame.SRCALPHA)
        self.__textures = textures
        self.__application = application
        self.__font = font
        self.__state = lambda mouse_pos: self.__menu(mouse_pos)

        self.__current_mouse = pygame.mouse.get_pressed()
        self.__previous_mouse = self.__current_mouse

        self.__cursor = False
        self.__track_slider = False
        
        self.__maps = []

        path = os.getcwd() + "/content/maps"

        # Traverse the map directory
        for root, dirs, files in os.walk(path):
            for file in files:
                # Check the extension of files
                if file.endswith('.json'):
                    # Add map file to available maps
                    self.__maps.append(file)

    def render(self, target: pygame.Surface):
        self.__current_mouse = pygame.mouse.get_pressed()
        self.__cursor = False

        self.__unscaled.fill(pygame.Color(0, 0, 0, 0))

        # Mouse left-click released
        if not(self.__current_mouse[0]) and self.__previous_mouse[0]:
            self.__track_slider = False

        view_width = 320
        view_height = 180

        window_width, window_height = pygame.display.get_surface().get_size()
        scale = min(window_width / view_width, window_height / view_height)

        bar_width = int((window_width - int(view_width * scale)) / 2)
        bar_height = int((window_height - int(view_height * scale)) / 2)

        mouse_pos = (int((pygame.mouse.get_pos()[0] - bar_width) / scale), int((pygame.mouse.get_pos()[1] - bar_height) / scale))

        if self.__state != None:
            self.__state(mouse_pos)
        
        #region Draw cursor
        
        if self.__cursor:
            sprite = self.__textures.subsurface(HOVER)
        else:
            sprite = self.__textures.subsurface(NONE)
        self.__unscaled.blit(sprite, (mouse_pos[0] - 4, mouse_pos[1] - 4))

        #endregion

        scaled = pygame.transform.scale(self.__unscaled, (target.get_width(), target.get_height()))
        target.blit(scaled, (0, 0))
        
        self.__previous_mouse = self.__current_mouse

    def __text_handler(self, mouse_pos, texts, states, rect, property = "", percentage = True):
        colour = pygame.Color("#A663CC")

        # Draw outline
        pygame.draw.rect(self.__unscaled, pygame.Color("#A663CC"), pygame.Rect(rect.x - 2, rect.y - 1, rect.width + 4, rect.height * len(texts) + 3), 1)

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
                self.__font.render(self.__unscaled, str(value).upper(), pygame.Vector2(rect.x, rect.y), colour)

            elif text == "SLIDER": 
                value = SETTINGS[property]

                if percentage: 
                    denominator = 2
                    percent = value
                else:
                    denominator = 1
                    lower_bound = SETTINGS[property + "LowerBound"]
                    upper_bound = SETTINGS[property + "UpperBound"] - lower_bound
                    percent = (math.degrees(value) - lower_bound) / upper_bound

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

                pygame.draw.rect(self.__unscaled, pygame.Color("#A663CC"), slider_bar)
                pygame.draw.rect(self.__unscaled, colour, slider_rect)

                if percentage:
                    number = str(round(percent * 100)) + "%"
                else:
                    number = str(round(percent * upper_bound + lower_bound)) + "°"
                self.__font.render(self.__unscaled, number, pygame.Vector2(rect.x, rect.y), colour)
            
            else:                
                if rect.collidepoint(mouse_pos):
                    colour = pygame.Color("#B298DC")
                    self.__cursor = True
                    # Mouse left-click pressed
                    if self.__current_mouse[0] and not(self.__previous_mouse[0]):
                        self.__state = states[i]
                else:
                    colour = pygame.Color("#A663CC")
                self.__font.render(self.__unscaled, text, pygame.Vector2(rect.x, rect.y), colour)
            rect.y += 8

    def __menu(self, mouse_pos):
        texts = ["START", "OPTIONS", "ABOUT", "EXIT"]

        states = [lambda mouse_pos: self.__start(mouse_pos), 
                  lambda mouse_pos: self.__options(mouse_pos), 
                  lambda mouse_pos: self.__about(mouse_pos),
                  lambda mouse_pos: self.__exit(mouse_pos)]
        
        rect = pygame.Rect(132, 96, 55, 8)

        self.__text_handler(mouse_pos, texts, states, rect)

    def __start(self, mouse_pos):
        texts = []
        states = []
        length = 0

        for map in self.__maps:
            texts.append(map[:-5].upper())
            states.append(lambda mouse_pos: None)
            if len(map[:-5]) > length:
                length = len(map[:-5])

        texts.append("BACK")
        states.append(lambda mouse_pos: self.__menu(mouse_pos))
        
        # Draw the title        
        self.__font.render(self.__unscaled, "START", pygame.Vector2(140, 85), pygame.Color("#A663CC"))

        rect = pygame.Rect(160 - (length * 8) / 2, 95, length * 8 - 1, 8)

        # Draw outline
        pygame.draw.rect(self.__unscaled, pygame.Color("#A663CC"), pygame.Rect(rect.x - 2, rect.y - 1, rect.width + 4, rect.height * len(texts) + 3), 1)

        for i, text in enumerate(texts):
            if rect.collidepoint(mouse_pos):
                colour = pygame.Color("#B298DC")
                self.__cursor = True
                # Mouse left-click pressed
                if self.__current_mouse[0] and not(self.__previous_mouse[0]):
                    if text == "BACK":
                        self.__state = states[i]
                    else:
                        self.__application.load_level("content/maps/" + self.__maps[i])
            else:
                colour = pygame.Color("#A663CC")
            
            try:
                self.__font.render(self.__unscaled, text, pygame.Vector2(rect.x, rect.y), colour)
            except KeyError as symbol:
                print("ERROR: Symbol " + str(symbol) + " within file name is not in the font!")
            
            rect.y += 8

        #self.__application.load_level("content/map.json")
    
    def __options(self, mouse_pos):
        texts = ["SENSITIVITY", "FOV", "PLAYER SPEED", "VIEW MODE", "LIGHTING", "LETTERBOX", "MENU SPIN", "BACK"]
        
        states = [lambda mouse_pos: self.__sensitivity(mouse_pos), 
                  lambda mouse_pos: self.__fov(mouse_pos), 
                  lambda mouse_pos: self.__player_speed(mouse_pos),
                  lambda mouse_pos: self.__view_mode(mouse_pos),
                  lambda mouse_pos: self.__lighting(mouse_pos),
                  lambda mouse_pos: self.__letterbox(mouse_pos),
                  lambda mouse_pos: self.__menu_spin(mouse_pos),
                  lambda mouse_pos: self.__menu(mouse_pos)]

        rect = pygame.Rect(112, 95, 95, 8)

        # Draw the title        
        self.__font.render(self.__unscaled, "OPTIONS", pygame.Vector2(132, 85), pygame.Color("#A663CC"))

        self.__text_handler(mouse_pos, texts, states, rect)

    def __about(self, mouse_pos):
        texts = ["RENDERING A PSEUDO 3D PRO-", 
                 "-JECTION BASED ON A 2D MAP", 
                 "", 
                 "MOVEMENT:WASD KEYS", 
                 "CAMERA:ARROW KEYS OR MOUSE", 
                 "", 
                 "DEVELOPED BY:ZAIN AKRAM"]
        
        colour = pygame.Color("#A663CC")
        rect = pygame.Rect(56, 95, 207, 65)
        back_rect = pygame.Rect(144, 152, 32, 8)

        # Draw outline
        pygame.draw.rect(self.__unscaled, pygame.Color("#A663CC"), pygame.Rect(rect.x - 2, rect.y - 1, rect.width + 4, rect.height + 3), 1)

        # Draw the title        
        self.__font.render(self.__unscaled, "ABOUT", pygame.Vector2(140, 85), pygame.Color("#A663CC"))

        for text in texts:
            self.__font.render(self.__unscaled, text, pygame.Vector2(rect.x, rect.y), colour)
            rect.y += 8

        # Draw the back button
        if back_rect.collidepoint(mouse_pos):
            colour = pygame.Color("#B298DC")
            self.__cursor = True
            # Mouse left-click pressed
            if self.__current_mouse[0] and not(self.__previous_mouse[0]):
                self.__state = lambda mouse_pos: self.__menu(mouse_pos)
        else:
            colour = pygame.Color("#A663CC")
        self.__font.render(self.__unscaled, "BACK", pygame.Vector2(back_rect.x, back_rect.y), colour)

    def __exit(self, mouse_pos):
        self.__application.is_running = False

    def __sensitivity(self, mouse_pos):
        texts = ["SLIDER", "BACK"]
        
        states = [lambda mouse_pos: None, 
                  lambda mouse_pos: self.__options(mouse_pos)]    
            
        rect = pygame.Rect(112, 95, 95, 8)
        
        # Draw the title        
        self.__font.render(self.__unscaled, "SENSITIVTY", pygame.Vector2(120, 85), pygame.Color("#A663CC"))
        
        self.__text_handler(mouse_pos, texts, states, rect, "sensitivityMultiplier", True)

    def __fov(self, mouse_pos):
        texts = ["HFOV", "VFOV", "BACK"]

        states = [lambda mouse_pos: self.__hfov(mouse_pos),
                  lambda mouse_pos: self.__vfov(mouse_pos), 
                  lambda mouse_pos: self.__options(mouse_pos)]   

        rect = pygame.Rect(144, 95, 31, 8)

        # Draw the title        
        self.__font.render(self.__unscaled, "FOV", pygame.Vector2(148, 85), pygame.Color("#A663CC"))

        self.__text_handler(mouse_pos, texts, states, rect)

    def __hfov(self, mouse_pos):
        texts = ["SLIDER", "BACK"]

        states = [lambda mouse_pos: None, 
                  lambda mouse_pos: self.__fov(mouse_pos)]    
            
        rect = pygame.Rect(112, 95, 95, 8)
        
        # Draw the title        
        self.__font.render(self.__unscaled, "HFOV", pygame.Vector2(144, 85), pygame.Color("#A663CC"))

        self.__text_handler(mouse_pos, texts, states, rect, "hfov", False)

    def __vfov(self, mouse_pos):
        texts = ["SLIDER", "BACK"]

        states = [lambda mouse_pos: None, 
                  lambda mouse_pos: self.__fov(mouse_pos)]            
        
        rect = pygame.Rect(112, 95, 95, 8)
        
        # Draw the title
        self.__font.render(self.__unscaled, "VFOV", pygame.Vector2(144, 85), pygame.Color("#A663CC"))
        
        self.__text_handler(mouse_pos, texts, states, rect, "vfov", False)

    def __player_speed(self, mouse_pos):
        texts = ["SLIDER", "BACK"]

        states = [lambda mouse_pos: None, 
                  lambda mouse_pos: self.__options(mouse_pos)]           
        
        rect = pygame.Rect(112, 95, 95, 8)
        
        # Draw the title        
        self.__font.render(self.__unscaled, "PLAYER SPEED", pygame.Vector2(112, 85), pygame.Color("#A663CC"))

        self.__text_handler(mouse_pos, texts, states, rect, "playerSpeedMultiplier", True)

    def __view_mode(self, mouse_pos):
        texts = ["LINEAR", "FISH EYE", "CORRECTED", "BACK"]

        states = [lambda mouse_pos: self.__linear(mouse_pos), 
                  lambda mouse_pos: self.__fish_eye(mouse_pos), 
                  lambda mouse_pos: self.__corrected(mouse_pos), 
                  lambda mouse_pos: self.__options(mouse_pos)]   
            
        rect = pygame.Rect(124, 95, 71, 8)

        # Draw the title        
        self.__font.render(self.__unscaled, "VIEW MODE", pygame.Vector2(124, 85), pygame.Color("#A663CC"))

        self.__text_handler(mouse_pos, texts, states, rect)

    def __lighting(self, mouse_pos):
        texts = ["PIXEL", "ANGLE", "SECTOR", "BACK"]

        states = [lambda mouse_pos: self.__pixel(mouse_pos), 
                  lambda mouse_pos: self.__angle(mouse_pos), 
                  lambda mouse_pos: self.__sector(mouse_pos), 
                  lambda mouse_pos: self.__options(mouse_pos)]   
            
        rect = pygame.Rect(136, 95, 47, 8)

        # Draw the title        
        self.__font.render(self.__unscaled, "LIGHTING", pygame.Vector2(128, 85), pygame.Color("#A663CC"))

        self.__text_handler(mouse_pos, texts, states, rect)

    def __pixel(self, mouse_pos):
        if not(SETTINGS["pixelLightMode"]):
            texts = ["BOOL", "BACK"]
        else:
            texts = ["TRUE", "BACK"]
            SETTINGS["angleLightMode"] = False
            SETTINGS["sectorLightMode"] = False

        states = [lambda mouse_pos: self.__pixel(mouse_pos), 
                  lambda mouse_pos: self.__lighting(mouse_pos)]   
        
        rect = pygame.Rect(140, 95, 39, 8)

        # Draw the title        
        self.__font.render(self.__unscaled, "PIXEL", pygame.Vector2(140, 85), pygame.Color("#A663CC"))

        self.__text_handler(mouse_pos, texts, states, rect, "pixelLightMode")

    def __angle(self, mouse_pos):
        if not(SETTINGS["angleLightMode"]):
            texts = ["BOOL", "BACK"]
        else:
            texts = ["TRUE", "BACK"]
            SETTINGS["pixelLightMode"] = False
            SETTINGS["sectorLightMode"] = False

        states = [lambda mouse_pos: self.__angle(mouse_pos), 
                  lambda mouse_pos: self.__lighting(mouse_pos)]   
        
        rect = pygame.Rect(140, 95, 39, 8)

        # Draw the title        
        self.__font.render(self.__unscaled, "ANGLE", pygame.Vector2(140, 85), pygame.Color("#A663CC"))

        self.__text_handler(mouse_pos, texts, states, rect, "angleLightMode")

    def __sector(self, mouse_pos):
        if not(SETTINGS["sectorLightMode"]):
            texts = ["BOOL", "BACK"]
        else:
            texts = ["TRUE", "BACK"]
            SETTINGS["angleLightMode"] = False
            SETTINGS["pixelLightMode"] = False

        states = [lambda mouse_pos: self.__sector(mouse_pos), 
                  lambda mouse_pos: self.__lighting(mouse_pos)]   
        
        rect = pygame.Rect(140, 95, 39, 8)

        # Draw the title        
        self.__font.render(self.__unscaled, "SECTOR", pygame.Vector2(136, 85), pygame.Color("#A663CC"))

        self.__text_handler(mouse_pos, texts, states, rect, "sectorLightMode")

    def __linear(self, mouse_pos):
        if not(SETTINGS["linearViewMode"]):
            texts = ["BOOL", "BACK"]
        else:
            texts = ["TRUE", "BACK"]
            SETTINGS["fishEyeViewMode"] = False
            SETTINGS["correctedViewMode"] = False

        states = [lambda mouse_pos: self.__linear(mouse_pos), 
                  lambda mouse_pos: self.__view_mode(mouse_pos)]   
        
        rect = pygame.Rect(140, 95, 39, 8)

        # Draw the title        
        self.__font.render(self.__unscaled, "LINEAR", pygame.Vector2(136, 85), pygame.Color("#A663CC"))

        self.__text_handler(mouse_pos, texts, states, rect, "linearViewMode")

    def __fish_eye(self, mouse_pos):
        if not(SETTINGS["fishEyeViewMode"]):
            texts = ["BOOL", "BACK"]
        else:
            texts = ["TRUE", "BACK"]
            SETTINGS["linearViewMode"] = False
            SETTINGS["correctedViewMode"] = False

        states = [lambda mouse_pos: self.__fish_eye(mouse_pos), 
                  lambda mouse_pos: self.__view_mode(mouse_pos)]   
        
        rect = pygame.Rect(140, 95, 39, 8)

        # Draw the title        
        self.__font.render(self.__unscaled, "FISH EYE", pygame.Vector2(128, 85), pygame.Color("#A663CC"))

        self.__text_handler(mouse_pos, texts, states, rect, "fishEyeViewMode")

    def __corrected(self, mouse_pos):
        if not(SETTINGS["correctedViewMode"]):
            texts = ["BOOL", "BACK"]
        else:
            texts = ["TRUE", "BACK"]
            SETTINGS["linearViewMode"] = False
            SETTINGS["fishEyeViewMode"] = False

        states = [lambda mouse_pos: self.__corrected(mouse_pos), 
                  lambda mouse_pos: self.__view_mode(mouse_pos)]
        
        rect = pygame.Rect(140, 95, 39, 8)

        # Draw the title        
        self.__font.render(self.__unscaled, "CORRECTED", pygame.Vector2(124, 85), pygame.Color("#A663CC"))

        self.__text_handler(mouse_pos, texts, states, rect, "correctedViewMode")

    def __letterbox(self, mouse_pos):
        texts = ["BOOL", "BACK"]

        states = [lambda mouse_pos: None, 
                  lambda mouse_pos: self.__options(mouse_pos)]   
        
        rect = pygame.Rect(140, 95, 39, 8)

        # Draw the title        
        self.__font.render(self.__unscaled, "LETTERBOX", pygame.Vector2(124, 85), pygame.Color("#A663CC"))

        self.__text_handler(mouse_pos, texts, states, rect, "letterbox")

    def __menu_spin(self, mouse_pos):
        texts = ["BOOL", "BACK"]

        states = [lambda mouse_pos: None, 
                  lambda mouse_pos: self.__options(mouse_pos)]    
            
        rect = pygame.Rect(140, 95, 39, 8)

        # Draw the title        
        self.__font.render(self.__unscaled, "MENU SPIN", pygame.Vector2(124, 85), pygame.Color("#A663CC"))

        self.__text_handler(mouse_pos, texts, states, rect, "menuSpin")