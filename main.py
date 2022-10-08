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
HFOV = 85
VFOV = 580

COLOR = [ 
        pygame.Color("yellow"), 
        pygame.Color("pink"), 
        pygame.Color("purple"), 
        pygame.Color("orange") 
        ]

class Player:

    SPEED = 0.3
    ROTATION = 0.025

    def __init__(self, x, y, rotation):
        self.x = x
        self.y = y
        self.angle = rotation

    def update(self):
        mouse_x = pygame.mouse.get_rel()[0]
        keys_down = pygame.key.get_pressed()

        # Mouse rotation
        if (pygame.event.get_grab()):
            self.angle += mouse_x * 0.0035

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
    pygame.display.set_caption("DoomEngine")
    pygame.mouse.set_visible(False)
    clock = pygame.time.Clock()


    # Set display mode
    flags = pygame.DOUBLEBUF | pygame.RESIZABLE
    graphics = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
    graphics.set_alpha(None)
    target = pygame.Surface((VIEW_WIDTH, VIEW_HEIGHT))
    pygame.event.set_grab(True)

    top_view = pygame.Surface((98, 109))
    transformed_view = pygame.Surface((98, 109))
    world_view = pygame.Surface((98, 109))

    # Initialise objects
    player = Player(49, 49, 0)
    walls = [
            Wall(70, 20, 70, 70),
            Wall(70, 70, 20, 70),
            Wall(20, 70, 20, 20),
            Wall(20, 20, 70, 20)
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

        pygame.draw.rect(top_view, pygame.Color("blue"), pygame.Rect(0, 0, 98, 109), 1)

        # Draw the top down view
        target.blit(top_view, (6, 40))

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
            pygame.draw.line(transformed_view, pygame.Color(COLOR[n]), (49 - rx1, 49 - ry1), (49 - rx2, 49 - ry2))

        # Draw the player
        pygame.draw.line(transformed_view, pygame.Color("red"), (49, 49), (49, 44))
        transformed_view.set_at((49, 49), pygame.Color("green"))

        pygame.draw.rect(transformed_view, pygame.Color("green"), pygame.Rect(0, 0, 98, 109), 1)

        # Draw the transformed view
        target.blit(transformed_view, (111, 40))

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

                ''''''
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

                if not(49 + x1 > 1):
                    dx1 = 1 - 49
                    
                if not(49 + x1 < 96):
                    dx1 = 97 - 49

                if not(49 + x2 > 1):
                    dx2 = 1 - 49
                    
                if not(49 + x2 < 96):
                    dx2 = 97 - 49

                for x in range(int(dx1), int(dx2)):
                    ya = (x - x1) * (y2a - y1a) / (x2 - x1) + y1a
                    yb = (x - x1) * (y2b-y1b) / (x2-x1) + y1b

                    pygame.draw.line(world_view, pygame.Color("light blue"), (49 + x, 0), (49 + x, 49 + -ya)) # Ceiling
                    pygame.draw.line(world_view, pygame.Color("gray"), (49 + x, 49 + yb), (49 + x, 140)) # Floor

                    pygame.draw.line(world_view, pygame.Color(COLOR[n]), (49 + x, 49 + ya), (49 + x, 49 + yb)) # Wall


                pygame.draw.line(world_view, pygame.Color("red"), (49 + x1, 49 + y1a), (49 + x1, 49 + y1b)) # # Left
                pygame.draw.line(world_view, pygame.Color("red"), (49 + x2, 49 + y2a), (49 + x2, 49 + y2b)) # Right

        pygame.draw.rect(world_view, pygame.Color("cyan"), pygame.Rect(0, 0, 98, 109), 1)

        # Draw the world view
        target.blit(world_view, (216, 40))

        #endregion

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