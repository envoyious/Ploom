# PLOOM, 0.3 WIP
# Developed by Zain Akram

import pygame

class Font:
    def __init__(self, texture):
        self.__char_width = 8
        self.__char_order = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789%°:- "
        self.__characters = {}

        self.spacing = 0

        char_count = 0 
        for x in range(texture.get_width() + 8):
            if x != 0 and x % self.__char_width == 0:
                char = self.__clip(texture, x - self.__char_width, 0, self.__char_width, texture.get_height()) 
                self.__characters[self.__char_order[char_count]] = char
                if char_count < len(self.__char_order) + 1:
                    char_count += 1
    
    def __clip(self, surface, x, y, width, height):
        sprite = surface.subsurface(pygame.Rect(x, y, width, height))
        return sprite

    def render(self, target, text, posistion, colour = pygame.Color("White")):
        x_offset = 0
        text = text.upper()
        for n in text:
            letter = pygame.Surface((self.__characters[n].get_rect().width, self.__characters[n].get_rect().height), pygame.SRCALPHA, 32)
            letter.convert_alpha()
            letter.blit(self.__characters[n], (0, 0))
            letter.fill(colour, special_flags=pygame.BLEND_MIN)
            
            target.blit(letter, (posistion.x + x_offset, posistion.y))
            x_offset += self.__char_width + self.spacing