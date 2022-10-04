# DoomEngine, 0.00 WIP
# Developed by Zain Akram

import sys
import math
import pygame
import pygame.draw

# Screen size
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 400
VIEW_WIDTH = 320
VIEW_HEIGHT = 200

CLEAR_COLOR = (pygame.Color("black"))

FRAMERATE = 60

class Player:

    def __init__(self, x, y, rotation):
        self.x = x
        self.y = y
        self.angle = rotation

    def update(self):
        keys_down = pygame.key.get_pressed()

        # Left and right rotation
        if (keys_down[pygame.K_LEFT] and not(keys_down[pygame.K_LALT])):
            self.angle -= 0.1
        
        if (keys_down[pygame.K_RIGHT] and not(keys_down[pygame.K_LALT])):
            self.angle += 0.1

        # Backwards and forwards movement
        if (keys_down[pygame.K_UP]):
            self.x += math.cos(self.angle)
            self.y += math.sin(self.angle)

        
        if (keys_down[pygame.K_DOWN]):
            self.x -= math.cos(self.angle)
            self.y -= math.sin(self.angle)


        # Strafe left and right
        if ((keys_down[pygame.K_LEFT] and keys_down[pygame.K_LALT]) or keys_down[pygame.K_COMMA]):
            self.x += math.sin(self.angle)
            self.y -= math.cos(self.angle)
        
        if ((keys_down[pygame.K_RIGHT] and keys_down[pygame.K_LALT]) or keys_down[pygame.K_PERIOD]):
            self.x -= math.sin(self.angle)
            self.y += math.cos(self.angle)

        self.__previous_key = keys_down

class Wall:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

def main():
    # Inintialise pygame
    pygame.init()
    pygame.display.set_caption("DoomEngine")
    clock = pygame.time.Clock()

    # Set display mode
    flags = pygame.DOUBLEBUF | pygame.RESIZABLE
    graphics = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
    graphics.set_alpha(None)
    target = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT))

    top_view = pygame.Surface((99, 109))

    # Initialise objects
    player = Player(50, 50, 0)
    wall = Wall(70, 20, 70, 70)

    # Main loop
    is_running = True
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

        # Updating
        player.update()

        # Rendering
        graphics.fill(pygame.Color("black"))        
        target.fill(CLEAR_COLOR)

        pygame.draw.rect(top_view, pygame.Color("blue"), pygame.Rect(0, 0, 99, 109), 1)

        # Draw the wall
        pygame.draw.line(top_view, pygame.Color("yellow"), (wall.x1, wall.y1), (wall.x2, wall.y2))

        # Draw the player
        pygame.draw.line(top_view, pygame.Color("red"), (player.x, player.y), (int(math.cos(player.angle) * 5 + player.x), int(math.sin(player.angle) * 5 + player.y)))
        top_view.set_at((int(player.x), int(player.y)), pygame.Color("green"))

        # Draw the top down view
        target.blit(top_view, (4, 40))

        #region Render target resizing

        window_width, window_height = graphics.get_size()
        scale = min(window_width / VIEW_WIDTH, window_height / VIEW_HEIGHT)

        bar_width = int((window_width - int(VIEW_WIDTH * scale)) / 2)
        bar_height = int((window_height - int(VIEW_HEIGHT * scale)) / 2)

        resized = pygame.transform.scale(target, (int(VIEW_WIDTH * scale), int(VIEW_HEIGHT * scale)))
        graphics.blit(resized, (bar_width, bar_height))

        #endregion

        pygame.display.update()
        
        # Cap the framerate at 60 frames per second
        clock.tick(FRAMERATE)
        pygame.display.set_caption("DoomEngine, FPS: {}".format(clock.get_fps()))

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()