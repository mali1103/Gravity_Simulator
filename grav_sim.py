import math
import pygame

pygame.init()

# --- Simulation and UI constants ---
WIDTH, HEIGHT = 1500, 1000
GRAV_CONSTANT = 6.67430e-11
TIME_STEP = 1000
ZOOM_SCALE = 6e-11
SCALE = 1e-9
DEFAULT_MASS = 5e29

# --- State variables ---
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravitational Simulation")
clock = pygame.time.Clock()
myfont = pygame.font.SysFont("monospace", 20)

ZOOMED = False
PAUSED = False
input_active = False

velocity_x = velocity_y = None
mouse_x = mouse_y = start_x = start_y = sim_x = sim_y = 0
mass_text = ""
next_mass = DEFAULT_MASS


# --- Body class ---
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
        ax = fx / self.mass
        ay = fy / self.mass
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


# --- Helper functions ---
def handle_mass_input(event):
    global input_active, mass_text, next_mass
    if event.key == pygame.K_RETURN:
        input_active = False
        try:
            next_mass = float(mass_text)*(10**20)
        except ValueError:
            next_mass = DEFAULT_MASS
    elif event.key == pygame.K_BACKSPACE:
        mass_text = mass_text[:-1]
    else:
        if event.unicode.isdigit() or event.unicode in ".eE+-":
            mass_text += event.unicode


def start_position(pos):
    global PAUSED, start_x, start_y, sim_x, sim_y, velocity_x, velocity_y, velocity_magnitude, mouse_x, mouse_y
    current_scale = ZOOM_SCALE if ZOOMED else SCALE
    start_x, start_y = pos
    sim_x = (start_x - WIDTH // 2) / current_scale
    sim_y = (start_y - HEIGHT // 2) / current_scale
    velocity_x = velocity_y = 0
    velocity_magnitude = 0.0
    mouse_x, mouse_y = start_x, start_y
    PAUSED = True


def update_velocity(pos):
    global mouse_x, mouse_y, velocity_x, velocity_y, velocity_magnitude
    mouse_x, mouse_y = pos
    velocity_x = (mouse_x - start_x) * 10000
    velocity_y = (mouse_y - start_y) * 10000
    velocity_magnitude = math.sqrt(velocity_x**2 + velocity_y**2)


def draw_paused_ui():
    for body in planets:
        body.draw(screen)
    if velocity_x is not None and velocity_y is not None:
        label = myfont.render(
            f"Velocity: x={velocity_x:.2e} m/s, y={velocity_y:.2e} m/s, s={velocity_magnitude:.2e} m/s",
            True, (255, 255, 255))
        pygame.draw.aaline(screen, (255, 255, 255),
                           (start_x, start_y), (mouse_x, mouse_y))
        screen.blit(label, (20, 20))
    if input_active:
        mass_label = myfont.render(f"Mass: {mass_text}e20 kg", True, (255, 255, 0))
        screen.blit(mass_label, (1200, 20))


# --- Main simulation loop ---
planets = [
    # Body(0, 0, 0, 0, 1.989e30, 4, (255, 255, 0)),
]

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                ZOOMED = not ZOOMED
            for body in planets:
                body.trail = []
            if PAUSED and event.key == pygame.K_BACKSLASH:
                input_active = True
                mass_text = ""
            if input_active:
                handle_mass_input(event)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if PAUSED and not input_active:
                finish_x, finish_y = event.pos
                current_scale = ZOOM_SCALE if ZOOMED else SCALE
                planets.append(Body(sim_x, sim_y, velocity_x,
                                    velocity_y, next_mass, 5, (160, 110, 255)))
                PAUSED = False
            elif not input_active:
                start_position(event.pos)
        elif event.type == pygame.MOUSEMOTION and PAUSED:
            update_velocity(event.pos)

    screen.fill((0, 0, 0))
    if not PAUSED:
        for body in planets:
            body.update_position(planets)
            body.draw(screen)
    else:
        draw_paused_ui()
    pygame.display.flip()
    clock.tick(60)
pygame.QUIT
