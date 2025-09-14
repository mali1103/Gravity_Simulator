import math
import pygame

pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Camera Movable Grid Map")
clock = pygame.time.Clock()

SCALE = 1.0
GRID_SIZE = 50
WORLD_SIZE = 2000  # World is a square from -WORLD_SIZE/2 to +WORLD_SIZE/2

class CameraMap:
    def __init__(self):
        self.cam_x = 0
        self.cam_y = 0
        self.dragging = False
        self.drag_start_mouse = (0, 0)
        self.drag_start_cam = (0, 0)
        self.sphere_x = 0
        self.sphere_y = 0
        self.sphere_vx = 3
        self.sphere_vy = 2
        self.sphere_radius = 20
        self.sphere_color = (80, 200, 255)

    def world_to_screen(self, x, y):
        return int((x - self.cam_x) * SCALE + WIDTH // 2), int((y - self.cam_y) * SCALE + HEIGHT // 2)

    def screen_to_world(self, sx, sy):
        return (sx - WIDTH // 2) / SCALE + self.cam_x, (sy - HEIGHT // 2) / SCALE + self.cam_y

    def draw_grid(self):
        world_x0, world_y0 = self.screen_to_world(0, 0)
        world_x1, world_y1 = self.screen_to_world(WIDTH, HEIGHT)
        start_x = GRID_SIZE * math.floor(world_x0 / GRID_SIZE)
        end_x = GRID_SIZE * math.ceil(world_x1 / GRID_SIZE)
        start_y = GRID_SIZE * math.floor(world_y0 / GRID_SIZE)
        end_y = GRID_SIZE * math.ceil(world_y1 / GRID_SIZE)
        for x in range(int(start_x), int(end_x), GRID_SIZE):
            sx0, sy0 = self.world_to_screen(x, start_y)
            sx1, sy1 = self.world_to_screen(x, end_y)
            pygame.draw.line(screen, (60, 60, 60), (sx0, sy0), (sx1, sy1))
        for y in range(int(start_y), int(end_y), GRID_SIZE):
            sx0, sy0 = self.world_to_screen(start_x, y)
            sx1, sy1 = self.world_to_screen(end_x, y)
            pygame.draw.line(screen, (60, 60, 60), (sx0, sy0), (sx1, sy1))
        # Draw world border
        border_left_top = self.world_to_screen(-WORLD_SIZE/2, -WORLD_SIZE/2)
        border_right_bottom = self.world_to_screen(WORLD_SIZE/2, WORLD_SIZE/2)
        border_rect = pygame.Rect(
            border_left_top[0], border_left_top[1],
            border_right_bottom[0] - border_left_top[0],
            border_right_bottom[1] - border_left_top[1]
        )
        pygame.draw.rect(screen, (200, 50, 50), border_rect, 6)

    def clamp_camera(self):
        min_x = -WORLD_SIZE/2
        max_x = WORLD_SIZE/2
        min_y = -WORLD_SIZE/2
        max_y = WORLD_SIZE/2
        self.cam_x = max(min_x, min(self.cam_x, max_x))
        self.cam_y = max(min_y, min(self.cam_y, max_y))

    def update_sphere(self):
        self.sphere_x += self.sphere_vx
        self.sphere_y += self.sphere_vy
        left = -WORLD_SIZE/2 + self.sphere_radius
        right = WORLD_SIZE/2 - self.sphere_radius
        top = -WORLD_SIZE/2 + self.sphere_radius
        bottom = WORLD_SIZE/2 - self.sphere_radius
        if self.sphere_x < left:
            self.sphere_x = left
            self.sphere_vx *= -1
        if self.sphere_x > right:
            self.sphere_x = right
            self.sphere_vx *= -1
        if self.sphere_y < top:
            self.sphere_y = top
            self.sphere_vy *= -1
        if self.sphere_y > bottom:
            self.sphere_y = bottom
            self.sphere_vy *= -1

    def draw_sphere(self):
        sx, sy = self.world_to_screen(self.sphere_x, self.sphere_y)
        pygame.draw.circle(screen, self.sphere_color, (sx, sy), self.sphere_radius)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.dragging = True
                        self.drag_start_mouse = event.pos
                        self.drag_start_cam = (self.cam_x, self.cam_y)
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging = False
                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging:
                        mx, my = event.pos
                        dx = mx - self.drag_start_mouse[0]
                        dy = my - self.drag_start_mouse[1]
                        self.cam_x = self.drag_start_cam[0] - dx / SCALE
                        self.cam_y = self.drag_start_cam[1] - dy / SCALE
                        self.clamp_camera()
            screen.fill((20, 20, 20))
            self.draw_grid()
            self.update_sphere()
            self.draw_sphere()
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()

def main():
    CameraMap().run()
    pygame.quit()

if __name__ == "__main__":
    main()

