# PLOOM, 0.3 WIP
# Developed by Zain Akram

import pygame, pygame.draw

from settings import SETTINGS

class Options():
    def __init__(self, font, target, application):
        self.__target = target
        self.__application = application
        self.__font = font
        self.__state = lambda mouse_pos: self.menu(mouse_pos)

        self.__current_mouse = pygame.mouse.get_pressed()
        self.__previous_mouse = self.__current_mouse

        self.cursor = False

    def render(self):
        self.__current_mouse = pygame.mouse.get_pressed()
        self.cursor = False

        viewWidth = SETTINGS["viewWidth"]
        viewHeight = SETTINGS["viewHeight"]

        window_width, window_height = pygame.display.get_surface().get_size()
        scale = min(window_width / viewWidth, window_height / viewHeight)

        bar_width = int((window_width - int(viewWidth * scale)) / 2)
        bar_height = int((window_height - int(viewHeight * scale)) / 2)

        mouse_pos = (int((pygame.mouse.get_pos()[0] - bar_width) / scale), int((pygame.mouse.get_pos()[1] - bar_height) / scale))

        if self.__state != None:
            self.__state(mouse_pos)
        
        self.__previous_mouse = self.__current_mouse

    def menu(self, mouse_pos):
        texts = ["START", "OPTIONS", "ABOUT", "EXIT"]
        colour = pygame.Color("#A663CC")
        rect = pygame.Rect(132, 96, 55, 8)

        pygame.draw.rect(self.__target, pygame.Color("#A663CC"), pygame.Rect(rect.x - 2, rect.y - 1, rect.width + 4, rect.height * len(texts) + 3), 1)

        for text in texts:
            if rect.collidepoint(mouse_pos):
                colour = pygame.Color("#B298DC")
                self.cursor = True
                if self.__current_mouse[0] and not(self.__previous_mouse[0]):
                    if text == "START":
                        self.__state = lambda mouse_pos: self.start(mouse_pos)
                    elif text == "OPTIONS":
                        self.__state = lambda mouse_pos: self.options(mouse_pos)
                    elif text == "ABOUT":
                        self.__state = lambda mouse_pos: self.about(mouse_pos)
                    elif text == "EXIT":
                        self.__state = lambda mouse_pos: self.exit(mouse_pos)
            else:
                colour = pygame.Color("#A663CC")
            self.__font.render(self.__target, text, pygame.Vector2(rect.x, rect.y), colour)
            rect.y += 8

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 100), (128, 100))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 100), (319 - 128, 100))
        
        #pygame.draw.rect(self.target, pygame.Color("red"), rect, 1)

    def start(self, mouse_pos):
        self.__application.load_level("content/map.json")
    
    def options(self, mouse_pos):
        texts = ["SENSITIVITY", "HFOV", "VFOV", "PLAYER SPEED", "LETTERBOX", "MENU SPIN", "BACK"]
        colour = pygame.Color("#A663CC")
        rect = pygame.Rect(112, 95, 95, 8)

        self.__font.render(self.__target, "OPTIONS", pygame.Vector2(132, 85), pygame.Color("#A663CC"))
        pygame.draw.rect(self.__target, pygame.Color("#A663CC"), pygame.Rect(rect.x - 2, rect.y - 1, rect.width + 4, rect.height * len(texts) + 3), 1)

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 90), (130, 90))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 90), (319 - 130, 90))

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 100), (108, 100))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 100), (319 - 108, 100))

        for text in texts:
            if rect.collidepoint(mouse_pos):
                colour = pygame.Color("#B298DC")
                self.cursor = True
                if self.__current_mouse[0] and not(self.__previous_mouse[0]):
                    if text == "LETTERBOX":
                        self.__state = lambda mouse_pos: self.letterbox(mouse_pos)
                    elif text == "MENU SPIN":
                        self.__state = lambda mouse_pos: self.menu_spin(mouse_pos)
                    elif text == "BACK":
                        self.__state = lambda mouse_pos: self.menu(mouse_pos)
            else:
                colour = pygame.Color("#A663CC")
            self.__font.render(self.__target, text, pygame.Vector2(rect.x, rect.y), colour)
            rect.y += 8
        
    def about(self, mouse_pos):
        pass

    def exit(self, mouse_pos):
        self.__application.is_running = False

    def sensitivity(self, mouse_pos):
        pass

    def hfov(self, mouse_pos):
        pass

    def vfov(self, mouse_pos):
        pass

    def player_speed(self, mouse_pos):
        pass

    def letterbox(self, mouse_pos):
        texts = [str(SETTINGS["letterbox"]), "BACK"]
        colour = pygame.Color("#A663CC")
        rect = pygame.Rect(140, 95, 39, 8)

        self.__font.render(self.__target, "LETTERBOX", pygame.Vector2(124, 85), pygame.Color("#A663CC"))
        pygame.draw.rect(self.__target, pygame.Color("#A663CC"), pygame.Rect(rect.x - 2, rect.y - 1, rect.width + 4, rect.height * len(texts) + 3), 1)

        for text in texts:
            if rect.collidepoint(mouse_pos):
                colour = pygame.Color("#B298DC")
                self.cursor = True
                if self.__current_mouse[0] and not(self.__previous_mouse[0]):
                    if text.upper() == "TRUE" or text.upper() == "FALSE":
                        SETTINGS["letterbox"] = not(SETTINGS["letterbox"])
                    elif text == "BACK":
                        self.__state = lambda mouse_pos: self.options(mouse_pos)
            else:
                colour = pygame.Color("#A663CC")
            self.__font.render(self.__target, text, pygame.Vector2(rect.x, rect.y), colour)
            rect.y += 8

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 90), (122, 90))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 90), (319 - 122, 90))

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 100), (136, 100))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 100), (319 - 136, 100))

    def menu_spin(self, mouse_pos):
        texts = [str(SETTINGS["menuSpin"]), "BACK"]
        colour = pygame.Color("#A663CC")
        rect = pygame.Rect(140, 95, 39, 8)

        self.__font.render(self.__target, "MENU SPIN", pygame.Vector2(124, 85), pygame.Color("#A663CC"))
        pygame.draw.rect(self.__target, pygame.Color("#A663CC"), pygame.Rect(rect.x - 2, rect.y - 1, rect.width + 4, rect.height * len(texts) + 3), 1)

        for text in texts:
            if rect.collidepoint(mouse_pos):
                colour = pygame.Color("#B298DC")
                self.cursor = True
                if self.__current_mouse[0] and not(self.__previous_mouse[0]):
                    if text.upper() == "TRUE" or text.upper() == "FALSE":
                        SETTINGS["menuSpin"] = not(SETTINGS["menuSpin"])
                    elif text == "BACK":
                        self.__state = lambda mouse_pos: self.options(mouse_pos)
            else:
                colour = pygame.Color("#A663CC")
            self.__font.render(self.__target, text, pygame.Vector2(rect.x, rect.y), colour)
            rect.y += 8
        
        pygame.draw.line(self.__target, pygame.Color("red"), (0, 90), (122, 90))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 90), (319 - 122, 90))

        pygame.draw.line(self.__target, pygame.Color("red"), (0, 100), (136, 100))
        pygame.draw.line(self.__target, pygame.Color("red"), (319, 100), (319 - 136, 100))

class Slider():
    def __init__(self):
        pass