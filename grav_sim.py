import math
import pygame

pygame.init()
WIDTH, HEIGHT = 1500, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravitational Simulation")
clock = pygame.time.Clock()
infofont = pygame.font.SysFont("monospace", 14, bold=True)
labelfont = pygame.font.SysFont("monospace", 16, bold=True)
# --- Simulation and UI constants ---

GRAV_CONSTANT = 6.67430e-11
TIME_STEP = 1000
SCALE = 1e-9
DEFAULT_MASS = 1e20

# --- State variables ---
PAUSED = False
input_active = False

velocity_x = velocity_y = None
mouse_x = mouse_y = start_x = start_y = sim_x = sim_y = 0
mass_text = ""
next_mass = DEFAULT_MASS


def drawGrid():
    minor_grid_size = 20
    for x in range(0, WIDTH, minor_grid_size):
        for y in range(0, HEIGHT, minor_grid_size):
            rect = pygame.Rect(x, y, minor_grid_size, minor_grid_size)
            pygame.draw.rect(screen, (10, 10, 10), rect, 1)
    major_grid_size = 100 #Set the size of the grid block
    for x in range(0, WIDTH, major_grid_size):
        for y in range(0, HEIGHT, major_grid_size):
            rect = pygame.Rect(x, y, major_grid_size, major_grid_size)
            pygame.draw.rect(screen, (30, 30, 30), rect, 1)
    


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

        scale = SCALE
        self.trail.append((int(self.x * scale + WIDTH // 2),
                           int(self.y * scale + HEIGHT // 2)))
        if len(self.trail) > 2000:
            self.trail.pop(0)

    def draw(self, screen):
        if len(self.trail) > 1:
            pygame.draw.lines(screen, (50, 50, 50), False, self.trail, 1)
        scale = SCALE
        screen_x = int(self.x * scale + WIDTH // 2)
        screen_y = int(self.y * scale + HEIGHT // 2)
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
    scale = SCALE
    start_x, start_y = pos
    sim_x = (start_x - WIDTH // 2) / scale
    sim_y = (start_y - HEIGHT // 2) / scale
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


def label_list_bodies():
    """
    Displays a list of all active bodies in the top left corner.
    """
    y_offset = 50
    scale = SCALE
    for i, body in enumerate(planets):
        list_info = (
            f"{i}: x={body.x:.2e}, y={body.y:.2e}, "
            f"vx={body.vx:.2e}, vy={body.vy:.2e}, m={body.mass:.2e}"
        )
        list_of_bodies = infofont.render(list_info, True, (234,212,118))
        screen.blit(list_of_bodies, (20, y_offset + i * 13))
        label_info = f"{i}"
        label_for_body = labelfont.render(label_info, True, body.color)
        screen.blit(label_for_body, (int(body.x * scale + WIDTH // 2),
                                      int(body.y * scale + HEIGHT // 2) - 5 * body.radius))

    


def add_new_body():
    """
    For every body in planets, the body will be drawn on the screen.

    If the each component of the velocity has a value (is not None), then their value will be rendered on the screen
    along with the magnitude of the velocity vector. A line is also rendered between the placement point of the body
    and the mouses current position.

    If the variable input_active is True, i.e. the user is choosing the mass of the new body, a label will be
    generated showing the selected mass value.
    """
    for body in planets:
        body.draw(screen)
    if velocity_x is not None and velocity_y is not None:
        velocity_label = infofont.render(
            f"Velocity: x={velocity_x:.2e} m/s, y={velocity_y:.2e} m/s, s={velocity_magnitude:.2e} m/s",
            True, (255, 255, 255))
        pygame.draw.aaline(screen, (255, 255, 255),
                           (start_x, start_y), (mouse_x, mouse_y))
        screen.blit(velocity_label, (20, 20))
    if input_active:
        mass_label = infofont.render(f"Mass: {mass_text}e20 kg", True, (255, 255, 0))
        screen.blit(mass_label, (1200, 20))



def remove_offscreen_bodies():
    """
    Removes bodies that are off the screen in zoomed out view.
    """
    scale = SCALE
    bodies_to_remove = []
    for body in planets:
        screen_x = int(body.x * scale + WIDTH // 2)
        screen_y = int(body.y * scale + HEIGHT // 2)
        if (screen_x < 0 or screen_x > WIDTH or
            screen_y < 0 or screen_y > HEIGHT):
            bodies_to_remove.append(body)
    for body in bodies_to_remove:
        planets.remove(body)


def main():
    global PAUSED, input_active, velocity_x, velocity_y, mouse_x, mouse_y
    global start_x, start_y, sim_x, sim_y, mass_text, next_mass, planets
    planets = []
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
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
                    scale = SCALE
                    if next_mass <= 1e20:
                        body_size = 4
                        body_colour = (150, 150, 150)
                    elif next_mass <= 1e24:
                        body_size = 8
                        body_colour = (110, 110, 255)
                    elif next_mass <= 1e28:
                        body_size = 12
                        body_colour = (255, 110, 110)
                    else:
                        body_size = 16
                        body_colour = (255, 255, 200)
                    planets.append(Body(sim_x, sim_y, velocity_x,
                                        velocity_y, next_mass, body_size, body_colour))
                    PAUSED = False
                elif not input_active:
                    start_position(event.pos)
            elif event.type == pygame.MOUSEMOTION and PAUSED:
                update_velocity(event.pos)

        screen.fill((3, 3, 3))
        drawGrid()
        if not PAUSED:
            for body in planets:
                body.update_position(planets)
                body.draw(screen)
            remove_offscreen_bodies()
            label_list_bodies()
        else:
            add_new_body()
            label_list_bodies()
        pygame.display.flip()
        clock.tick(60)
    pygame.QUIT


if __name__ == "__main__":
    main()
