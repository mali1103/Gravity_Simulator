import math
import pygame

pygame.init()
WIDTH, HEIGHT = 1500, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravitational Simulation")
clock = pygame.time.Clock()

GRAV_CONSTANT = 6.67430e-11  # Gravitational constant
TIME_STEP = 1000  # Time step for simulation
ZOOM_SCALE = 6e-11  # Zoom scale for visualization
SCALE = 1e-9  # Scale to convert simulation units to screen units
ZOOMED = False  # Zoom state
PAUSED = False  # Game pause state
myfont = pygame.font.SysFont("monospace", 20)

velocity_x = velocity_y = None  # Add at the top, after other globals


class Body:
    def __init__(self, x, y, vx, vy, mass, radius, color):
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.mass = mass
        self.radius = radius
        self.color = color
        self.trail = []

    def update_position(self, bodies):
        fx = fy = 0
        for body in bodies:
            if body != self:
                dx = body.x - self.x
                dy = body.y - self.y
                distance = math.sqrt(dx*dx + dy*dy)
                if distance >= 6e6:
                    force = (GRAV_CONSTANT * self.mass *
                             body.mass) / (distance*distance)
                    fx += force * dx / distance
                    fy += force * dy / distance
        ax = (fx) / self.mass
        ay = (fy) / self.mass
        self.vx += ax * TIME_STEP
        self.vy += ay * TIME_STEP
        self.x += self.vx * TIME_STEP
        self.y += self.vy * TIME_STEP

        current_scale = ZOOM_SCALE if ZOOMED else SCALE

        self.trail.append((int(self.x * current_scale + WIDTH // 2),
                          int(self.y * current_scale + HEIGHT // 2)))
        if len(self.trail) > 2000:
            self.trail.pop(0)

    def draw(self, screen):
        if len(self.trail) > 1:
            pygame.draw.lines(screen, (50, 50, 50), False, self.trail, 1)

        current_scale = ZOOM_SCALE if ZOOMED else SCALE
        screen_x = int(self.x * current_scale + WIDTH // 2)
        screen_y = int(self.y * current_scale + HEIGHT // 2)

        pygame.draw.circle(screen, self.color,
                           (screen_x, screen_y), self.radius)


planets = [
    # Body(0, 0, 0, 0, 1.989e30, 4, (255, 255, 0)),  # Sun  (1.989e30 kg, 8 pixel radius (not used in calculations, just visual))
]

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                ZOOMED = not ZOOMED
            for body in planets:
                body.trail = []
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:  # Right mouse button
            if PAUSED:
                finish_x, finish_y = event.pos
                current_scale = ZOOM_SCALE if ZOOMED else SCALE
                planets.append(Body(sim_x, sim_y, velocity_x,
                               velocity_y, 5e29, 5, (160, 110, 255)))
                PAUSED = False
            else:
                start_x, start_y = event.pos
                current_scale = ZOOM_SCALE if ZOOMED else SCALE
                sim_x = (start_x - WIDTH // 2) / current_scale
                sim_y = (start_y - HEIGHT // 2) / current_scale
                PAUSED = True
                # Reset velocity values for new drag
                velocity_x = 0
                velocity_y = 0
                velocity_magnitude = 0.0  # <-- Add this line
                mouse_x = start_x
                mouse_y = start_y
        if event.type == pygame.MOUSEMOTION and PAUSED:
            mouse_x, mouse_y = event.pos
            velocity_x = (mouse_x - start_x) * 10000
            velocity_y = (mouse_y - start_y) * 10000
            velocity_magnitude = math.sqrt(velocity_x**2 + velocity_y**2)

    screen.fill((0, 0, 0))
    if not PAUSED:
        for body in planets:
            body.update_position(planets)
            body.draw(screen)
    else:
        for body in planets:
            body.draw(screen)
        if velocity_x is not None and velocity_y is not None:
            label = myfont.render(
                f"Velocity: x={velocity_x:.2e} m/s, y={velocity_y:.2e}, s={velocity_magnitude:.2e}",
                True, (255, 255, 255))
            pygame.draw.aaline(screen,(255,255,255),(start_x, start_y),(mouse_x, mouse_y))
            screen.blit(label, (20, 20))
    pygame.display.flip()
    clock.tick(60)
pygame.QUIT
