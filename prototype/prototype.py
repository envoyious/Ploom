# PROTOTYPE, 0.0 WIP
# Developed by Zain Akram

import sys
import math
import pygame
import pygame.draw

# Screen size
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 360
VIEW_WIDTH = 320
VIEW_HEIGHT = 180

CLEAR_COLOR = (pygame.Color("black"))

FRAMERATE = 60
HFOV = 103
VFOV = 620

COLOR = [ 
        pygame.Color("yellow"), 
        pygame.Color("pink"), 
        pygame.Color("purple"), 
        pygame.Color("orange") 
        ]

class Player:

    SPEED = 0.4
    ROTATION = 0.025
    SENSITIVITY = 0.0008

    def __init__(self, x, y, rotation):
        self.x = x
        self.y = y
        self.angle = rotation
        self.__previous_key = pygame.key.get_pressed()

    def update(self):
        mouse_x = pygame.mouse.get_rel()[0]
        keys_down = pygame.key.get_pressed()

        # Mouse rotation
        if (pygame.event.get_grab()):
            self.angle += mouse_x * self.SENSITIVITY

        # Left and right rotation
        if (keys_down[pygame.K_LEFT]):
            self.angle -= self.ROTATION
        
        if (keys_down[pygame.K_RIGHT]):
            self.angle += self.ROTATION

        # Backwards and forwards movement
        if (keys_down[pygame.K_UP] or keys_down[pygame.K_w]):
            self.x += math.cos(self.angle) * self.SPEED
            self.y += math.sin(self.angle) * self.SPEED

        
        if (keys_down[pygame.K_DOWN] or keys_down[pygame.K_s]):
            self.x -= math.cos(self.angle) * self.SPEED
            self.y -= math.sin(self.angle) * self.SPEED


        # Strafe left and right
        if (keys_down[pygame.K_a]):
            self.x += math.sin(self.angle) * self.SPEED
            self.y -= math.cos(self.angle) * self.SPEED
        
        if (keys_down[pygame.K_d]):
            self.x -= math.sin(self.angle) * self.SPEED
            self.y += math.cos(self.angle) * self.SPEED

        self.__previous_key = keys_down

class Wall:
    def __init__(self, x1, y1, x2, y2):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

def two_by_two_determinant(x1, y1, x2, y2):
    return x1 * y2 - y1 * x2

def intersect(x1, y1, x2, y2, x3, y3, x4, y4):
    x = two_by_two_determinant(x1, y1, x2, y2)
    y = two_by_two_determinant(x3, y3, x4, y4)
    det = two_by_two_determinant(x1 - x2, y1 - y2, x3 - x4, y3 - y4)
    x = two_by_two_determinant(x, x1 - x2, y, x3 - x4) / det
    y = two_by_two_determinant(x, y1 - y2, y, y3 - y4) / det
    return x, y

def main():
    # Inintialise pygame
    pygame.init()
    pygame.display.set_caption("PROTOTYPE")
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()


    # Set display mode
    flags = pygame.DOUBLEBUF | pygame.RESIZABLE
    graphics = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
    graphics.set_alpha(None)
    target = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT))
    pygame.event.set_grab(True)

    top_view = pygame.Surface((64, 64))
    transformed_view = pygame.Surface((64, 64))
    world_view = pygame.Surface((320, 180))

    # Initialise objects
    player = Player(32, 32, 0)
    walls = [
            Wall(57, 7, 57, 57),
            Wall(57, 57, 7, 57),
            Wall(7, 57, 7, 7),
            Wall(7, 7, 57, 7)
            ]

    # Main loop
    is_running = True
    while is_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.mouse.set_visible(not(pygame.mouse.get_visible()))
                    pygame.event.set_grab(not(pygame.event.get_grab()))

        # Updating
        player.update()

        # Rendering
        graphics.fill(pygame.Color("black"))        
        target.fill("black")

        top_view.fill(CLEAR_COLOR)
        transformed_view.fill(CLEAR_COLOR)
        world_view.fill(CLEAR_COLOR)

        #region Top down view

        # Draw the wall
        for n, wall in enumerate(walls):
            pygame.draw.line(top_view, pygame.Color(COLOR[n]), (wall.x1, wall.y1), (wall.x2, wall.y2))

        # Draw the player
        pygame.draw.line(top_view, pygame.Color("red"), (player.x, player.y), (int(math.cos(player.angle) * 5 + player.x), int(math.sin(player.angle) * 5 + player.y)))
        top_view.set_at((int(player.x), int(player.y)), pygame.Color("green"))

        pygame.draw.rect(top_view, pygame.Color("red"), pygame.Rect(0, 0, 64, 64), 1)

        #endregion

        #region Transformed view

        for n, wall in enumerate(walls):
            # Transforming wall vertexes to be relative to the player
            tx1 = wall.x1 - player.x
            ty1 = wall.y1 - player.y
            tx2 = wall.x2 - player.x
            ty2 = wall.y2 - player.y

            # Rotating the vertexes around the player
            rx1 = tx1 * math.sin(player.angle) - ty1 * math.cos(player.angle)
            rx2 = tx2 * math.sin(player.angle) - ty2 * math.cos(player.angle)
            ry1 = tx1 * math.cos(player.angle) + ty1 * math.sin(player.angle)
            ry2 = tx2 * math.cos(player.angle) + ty2 * math.sin(player.angle)

            # Draw the wall
            pygame.draw.line(transformed_view, pygame.Color(COLOR[n]), (32 - rx1, 32 - ry1), (32 - rx2, 32 - ry2))

        # Draw the player
        pygame.draw.line(transformed_view, pygame.Color("red"), (32, 32), (32, 27))
        transformed_view.set_at((32, 32), pygame.Color("green"))

        pygame.draw.rect(transformed_view, pygame.Color("red"), pygame.Rect(0, 0, 64, 64), 1)

        #endregion
        
        #region World view
        
        for n, wall in enumerate(walls):
            # Transforming wall vertexes to be relative to the player
            tx1 = wall.x1 - player.x
            ty1 = wall.y1 - player.y
            tx2 = wall.x2 - player.x
            ty2 = wall.y2 - player.y

            # Rotating the vertexes around the player
            rx1 = tx1 * math.sin(player.angle) - ty1 * math.cos(player.angle)
            rx2 = tx2 * math.sin(player.angle) - ty2 * math.cos(player.angle)
            ry1 = tx1 * math.cos(player.angle) + ty1 * math.sin(player.angle)
            ry2 = tx2 * math.cos(player.angle) + ty2 * math.sin(player.angle)

            # Clip the walls
            if ry1 > 0 or ry2 > 0:
                nearz = 0.0001
                farz = 5
                nearside = 0.0001
                farside = 1000

                ix1, iy1 = intersect(rx1, ry1, rx2, ry2, -nearside, nearside, -farside, farz)
                ix2, iy2 = intersect(rx1, ry1, rx2, ry2, nearside, nearside, farside, farz)

                if ry1 <= 0:
                    if iy1 > 0:
                        rx1 = ix1
                        ry1 = iy1
                    else:
                        rx1 = ix2
                        ry1 = iy2
                
                if ry2 <= 0:
                    if iy1 > 0:
                        rx2 = ix1
                        ry2 = iy1
                    else:
                        rx2 = ix2
                        ry2 = iy2

                # Transforming 3D coordinate onto the 2D plane
                x1 = -rx1 * HFOV / ry1
                y1a = -VFOV / ry1 
                y1b = VFOV / ry1

                x2 = -rx2 * HFOV / ry2
                y2a = -VFOV / ry2
                y2b = VFOV / ry2

                # Clip segments off screen
                dx1 = x1
                dx2 = x2

                if not(180 + x1 > 0):
                    dx1 = -180
                    
                if not(180 + x1 < 360):
                    dx1 = 180

                if not(180 + x2 > 0):
                    dx2 = -180
                    
                if not(180 + x2 < 360):
                    dx2 = 180

                for x in range(int(dx1), int(dx2)):
                    ya = (x - x1) * (y2a - y1a) / (x2 - x1) + y1a
                    yb = (x - x1) * (y2b-y1b) / (x2-x1) + y1b

                    pygame.draw.line(world_view, pygame.Color("light blue"), (180 + x, 0), (180 + x, 180 + -ya)) # Ceiling
                    pygame.draw.line(world_view, pygame.Color("snow"), (180 + x, 180 + yb), (180 + x, 90)) # Floor

                    pygame.draw.line(world_view, pygame.Color(COLOR[n]), (180 + x, 90 + ya), (180 + x, 90 + yb)) # Wall


                pygame.draw.line(world_view, pygame.Color("red"), (180 + x1, 90 + y1a), (180 + x1, 90 + y1b)) # # Left
                pygame.draw.line(world_view, pygame.Color("red"), (180 + x2, 90 + y2a), (180 + x2, 90 + y2b)) # Right

        #pygame.draw.rect(world_view, pygame.Color("cyan"), pygame.Rect(0, 0, 98, 109), 1)

        #endregion

        # Draw the world view
        target.blit(world_view, (0, 0))

        # Draw the transformed view
        target.blit(transformed_view, (4, 4))

        # Draw the top down view
        target.blit(top_view, (4, 72))

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
        pygame.display.set_caption("PROTOTYPE, FPS: {}".format(clock.get_fps()))

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()