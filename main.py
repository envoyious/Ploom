# PLOOM, 0.3 WIP
# Developed by Zain Akram

import pygame, pygame.draw

from engine import Engine
from game import Game
from settings import SETTINGS

class App(Engine):
    def initialise(self):
        super().initialise()

        self._window_width = SETTINGS["windowWidth"]
        self._window_height = SETTINGS["windowHeight"]

        # Set display mode
        self._flags = pygame.DOUBLEBUF | pygame.RESIZABLE
        self._caption = "PLOOM"
        self._mouse_visible = False
        self._mouse_grab = True
        self._framerate = SETTINGS["framerate"]

        self.scene = Game("content/map.json")

    def update(self, delta_time):
        self.scene.update(delta_time)
        super().update(delta_time)
    
    def render(self):
        self._graphics.fill(pygame.Color("black"))

        viewWidth = SETTINGS["viewWidth"]
        viewHeight = SETTINGS["viewHeight"]

        self.scene.render()

        #region Render target resizing

        target = self.scene.target
        window_width, window_height = self._graphics.get_size()
        scale = min(window_width / viewWidth, window_height / viewHeight)

        bar_width = int((window_width - int(viewWidth * scale)) / 2)
        bar_height = int((window_height - int(viewHeight * scale)) / 2)

        if SETTINGS["letterbox"]:
            # Adds black bars to either side of the screen
            resized = pygame.transform.scale(target, (int(viewWidth * scale), int(viewHeight * scale)))
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