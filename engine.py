# PLOOM, 0.3 WIP
# Developed by Zain Akram

import sys, time
import pygame, pygame.draw

class Engine:
    instance = None

    def __init__(self):
        # Static properties
        self.instance = self

        # Protected properties
        self._window_width = 640
        self._window_height = 360
        self._caption = "Engine"
        self._mouse_visible = True
        self._mouse_grab = False
        self._graphics = None
        self._flags = 0
        self._framerate = 60
        self._fixed_time_step = True

        # Public properties
        self.is_running = True

    # Abstract methods
    def initialise(self):
        pass

    def load_content(self):
        pass
    
    def update(self, delta_time):
        pass
    
    def render(self):
        pass
    
    # Public methods
    def run(self):
        # Inintialise pygame
        pygame.init()
        self.initialise()
        
        pygame.display.set_caption(self._caption)
        pygame.mouse.set_visible(self._mouse_visible)
        clock = pygame.time.Clock()

        self._graphics = pygame.display.set_mode((self._window_width, self._window_height), self._flags)
        self._graphics.set_alpha(None)

        pygame.event.set_grab(self._mouse_grab)

        self.load_content()

        prev_time = time.time()
        delta_time = 0

        # Main loop
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
            
            # Calculate the interval in seconds from the last frame to the current one
            current_time = time.time()
            delta_time = current_time - prev_time
            prev_time = current_time

            # Updating
            self.update(delta_time)

            # Rendering
            self.render()

            # Cap the framerate
            if self._fixed_time_step:
                clock.tick(self._framerate)
            else:
                clock.tick()
            pygame.display.set_caption(str(self._caption + ", FPS: {}").format(clock.get_fps()))
    

        pygame.quit()
        sys.exit()        

class Scene:
    def __init__(self, application):
        self.application = application
        self.target = pygame.Surface((640, 360))

    def load_content(self):
        pass

    def update(self, delta_time):
        pass

    def render(self):
        pass