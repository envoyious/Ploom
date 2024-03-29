# PLOOM, 1.0 FINAL
# Developed by Zain Akram

import pygame, pygame.draw

from engine import Engine
from game import Game
from menu import Menu
from settings import SETTINGS

class App(Engine):
    def initialise(self):
        super().initialise()

        self._window_width = SETTINGS["windowWidth"]
        self._window_height = SETTINGS["windowHeight"]

        # Set display mode
        self._flags = pygame.DOUBLEBUF | pygame.RESIZABLE
        self._caption = "Ploom"
        self._mouse_visible = False
        self._mouse_grab = True
        self._framerate = SETTINGS["framerate"]
        self._fixed_time_step = SETTINGS["fixedTimeStep"]

        #self.scene = Game(self.instance, "content/map.json")
        self.__scene = Menu(self.instance)

    def load_level(self, path):
        self.__scene = Game(self.instance, path)
        self.__scene.load_content()

    def load_content(self):
        self._icon = pygame.image.load("content/icon.png").convert()
        self.__scene.load_content()
        super().load_content()

    def update(self, delta_time):
        self.__scene.update(delta_time)
        super().update(delta_time)
    
    def render(self):
        self._graphics.fill(pygame.Color("black"))

        view_width = SETTINGS["viewWidth"]
        view_height = SETTINGS["viewHeight"]

        self.__scene.render()

        #region Render target resizing

        target = self.__scene.get_target()
        window_width, window_height = self._graphics.get_size()
        scale = min(window_width / view_width, window_height / view_height)

        bar_width = int((window_width - int(view_width * scale)) / 2)
        bar_height = int((window_height - int(view_height * scale)) / 2)

        if SETTINGS["letterbox"]:
            # Adds black bars to either side of the screen
            resized = pygame.transform.scale(target, (int(view_width * scale), int(view_height * scale)))
            self._graphics.blit(resized, (bar_width, bar_height))
        else:
            # Stretches image to fill the whole screen
            resized = pygame.transform.scale(target, (window_width, window_height))
            self._graphics.blit(resized, (0, 0))

        #endregion
        
        pygame.display.update()
        super().render()

def main():
    app = App()
    app.run()

if __name__ == "__main__":
    main()