import math
import pygame

pygame.init()
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravity Sim on Movable Map")
clock = pygame.time.Clock()
infofont = pygame.font.SysFont("monospace", 12, bold=True)
labelfont = pygame.font.SysFont("monospace", 16, bold=True)

GRID_SIZE = 50
WORLD_SIZE = 2000
GRAV_CONSTANT = 6.67430e-11
TIME_STEP = 1000
SCALE = 0.5
DEFAULT_MASS = 1e20


class Body:
    def __init__(self, start_x, start_y, vx, vy, mass, radius, color):
        self.x, self.y = start_x, start_y
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

        self.trail.append((self.x, self.y))
        if len(self.trail) > 2000:
            self.trail.pop(0)

    def draw(self, screen, cam_x, cam_y):
        if len(self.trail) > 1:
            trail_pts = [Simulation.world_to_screen(x, y, cam_x, cam_y)
                         for x, y in self.trail]
            pygame.draw.lines(screen, (50, 50, 50), False, trail_pts, 1)
        screen_x, screen_y = Simulation.world_to_screen(self.x, self.y, cam_x, cam_y)
        pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.radius)

class Simulation:
    def __init__(self):
        self.paused = False
        self.input_active = False
        self.velocity_x = None
        self.velocity_y = None
        self.velocity_magnitude = 0.0
        self.mouse_x = 0
        self.mouse_y = 0
        self.start_x = 0
        self.start_y = 0
        self.sim_x = 0
        self.sim_y = 0
        self.mass_text = ""
        self.next_mass = DEFAULT_MASS
        self.planets = []
        # Camera state
        self.cam_x = 0
        self.cam_y = 0
        self.dragging = False
        self.drag_start_mouse = (0, 0)
        self.drag_start_cam = (0, 0)

    @staticmethod
    def world_to_screen(x, y, cam_x, cam_y):
        converted_x = int((x - cam_x) * SCALE + WIDTH // 2)
        converted_y = int((y - cam_y) * SCALE + HEIGHT // 2)
        return converted_x, converted_y
    @staticmethod
    def screen_to_world(sx, sy, cam_x, cam_y):
        return (sx - WIDTH // 2) / SCALE + cam_x, (sy - HEIGHT // 2) / SCALE + cam_y

    def draw_grid(self):
        world_x0, world_y0 = self.screen_to_world(0, 0, self.cam_x, self.cam_y)
        world_x1, world_y1 = self.screen_to_world(WIDTH, HEIGHT, self.cam_x, self.cam_y)
        start_x = GRID_SIZE * math.floor(world_x0 / GRID_SIZE)
        end_x = GRID_SIZE * math.ceil(world_x1 / GRID_SIZE)
        start_y = GRID_SIZE * math.floor(world_y0 / GRID_SIZE)
        end_y = GRID_SIZE * math.ceil(world_y1 / GRID_SIZE)
        for x in range(int(start_x), int(end_x), GRID_SIZE):
            sx0, sy0 = self.world_to_screen(x, start_y, self.cam_x, self.cam_y)
            sx1, sy1 = self.world_to_screen(x, end_y, self.cam_x, self.cam_y)
            pygame.draw.line(screen, (60, 60, 60), (sx0, sy0), (sx1, sy1))
        for y in range(int(start_y), int(end_y), GRID_SIZE):
            sx0, sy0 = self.world_to_screen(start_x, y, self.cam_x, self.cam_y)
            sx1, sy1 = self.world_to_screen(end_x, y, self.cam_x, self.cam_y)
            pygame.draw.line(screen, (60, 60, 60), (sx0, sy0), (sx1, sy1))
        # Draw world border
        border_left_top = self.world_to_screen(-WORLD_SIZE/2, -WORLD_SIZE/2, self.cam_x, self.cam_y)
        border_right_bottom = self.world_to_screen(WORLD_SIZE/2, WORLD_SIZE/2, self.cam_x, self.cam_y)
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

    def handle_mass_input(self, event):
        if event.key == pygame.K_RETURN:
            self.input_active = False
            try:
                self.next_mass = float(self.mass_text)*(10**20)
            except ValueError:
                self.next_mass = DEFAULT_MASS
        elif event.key == pygame.K_BACKSPACE:
            self.mass_text = self.mass_text[:-1]
        else:
            if event.unicode.isdigit() or event.unicode in ".eE+-":
                self.mass_text += event.unicode

    def start_position(self, pos):
        self.start_x, self.start_y = pos
        self.sim_x, self.sim_y = self.screen_to_world(
            self.start_x, self.start_y, self.cam_x, self.cam_y)
        self.velocity_x = self.velocity_y = 0
        self.velocity_magnitude = 0.0
        self.mouse_x, self.mouse_y = self.start_x, self.start_y
        self.paused = True

    def update_velocity(self, pos):
        self.mouse_x, self.mouse_y = pos
        sim_mouse_x, sim_mouse_y = self.screen_to_world(
            self.mouse_x, self.mouse_y, self.cam_x, self.cam_y)
        self.velocity_x = (sim_mouse_x - self.sim_x) * 10000
        self.velocity_y = (sim_mouse_y - self.sim_y) * 10000
        self.velocity_magnitude = math.sqrt(
            self.velocity_x**2 + self.velocity_y**2)

    def label_list_bodies(self):
        y_offset = 50
        for i, body in enumerate(self.planets):
            list_info = (
                f"{i}: x={body.x:.2e}, y={body.y:.2e}, "
                f"vx={body.vx:.2e}, vy={body.vy:.2e}, m={body.mass:.2e}"
            )
            list_of_bodies = infofont.render(list_info, True, (234, 212, 118))
            screen.blit(list_of_bodies, (20, y_offset + i * 13))
            label_info = f"{i}"
            sx, sy = self.world_to_screen(body.x, body.y, self.cam_x, self.cam_y)
            label_for_body = labelfont.render(label_info, True, body.color)
            screen.blit(label_for_body, (sx, sy - 5 * body.radius))

    def add_new_body(self):
        for body in self.planets:
            body.draw(screen, self.cam_x, self.cam_y)
        if self.velocity_x is not None and self.velocity_y is not None:
            velocity_label = infofont.render(
                f"Velocity: x={self.velocity_x:.2e} m/s, y={self.velocity_y:.2e} m/s, s={self.velocity_magnitude:.2e} m/s",
                True, (255, 255, 255))
            pygame.draw.aaline(screen, (255, 255, 255),
                               (self.start_x, self.start_y), (self.mouse_x, self.mouse_y))
            screen.blit(velocity_label, (20, 20))
        if self.input_active:
            mass_label = infofont.render(
                f"Mass: {self.mass_text}e20 kg", True, (255, 255, 0))
            screen.blit(mass_label, (800, 20))

    def remove_offscreen_bodies(self):
        bodies_to_remove = []
        for body in self.planets:
            if (abs(body.x) > WORLD_SIZE/2 or abs(body.y) > WORLD_SIZE/2):
                bodies_to_remove.append(body)
        for body in bodies_to_remove:
            self.planets.remove(body)

    def run(self):
        """

        This is the main simulation loop.
        
        Parameters:
        ------------------------------------------------------------------------
        None

        Returns:
        ------------------------------------------------------------------------
        None

        Description:
        ------------------------------------------------------------------------
        On start, it sets running to True and therefore enters a loop. At the
        start of the loop, for each event in the pygame event queue:

            If the user has requested to quit, running is set to False and the 
            loop ends.
            
            Else, if the the user has pressed a key, the trails are cleared and 
            the key type is checked:
            
                If the user pressed the backslash key, input mode is activated 
                and the mass text is cleared.
            
            Else, if the user has pressed a mouse buton:
            
                If the left button is pressed (event.button == 1), dragging mode
                is activated and the starting mouse position and camera position
                are recorded.
            
                Else if the right button is pressed (event.button == 3):
    
                    and the simulation is paused and not in input mode, a new 
                    body is created at the starting position with the specified 
                    mass and velocity, and the simulation is unpaused.

                    and the right button is pressed and not in input mode, the 
                    starting position is recorded and the simulation is paused.

            Else, if the user has released a mouse button:
                
                If the left mouse button is released, dragging mode is 
                deactivated.

            Else if the the user moves the mouse:

                If dragging mode is active, the camera position is updated to 
                the new position based on the mouse movement whilst keeping the 
                camera clamped to the world bounds.

                Else if the simulation is paused, the velocity vector is updated 
                based on the current mouse position.

        The screen background is filled and the grid is drawn.
        
        If the simulation is not paused, each body is updated and drawn,
        offscreen bodies are removed and body labels are drawn.

        Else, the new body preview is drawn and body labels are drawn.

        The display is updated and the clock updates.

        """
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    for body in self.planets:
                        body.trail = []
                    if self.paused and event.key == pygame.K_BACKSLASH:
                        self.input_active = True
                        self.mass_text = ""
                    if self.input_active:
                        self.handle_mass_input(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.dragging = True
                        self.drag_start_mouse = event.pos
                        self.drag_start_cam = (self.cam_x, self.cam_y)
                    elif event.button == 3:
                        if self.paused and not self.input_active:
                            finish_x, finish_y = event.pos
                            if self.next_mass <= 1e20:
                                body_size = 4
                                body_colour = (100, 100, 100)
                            elif self.next_mass <= 1e24:
                                body_size = 8
                                body_colour = (110, 110, 255)
                            elif self.next_mass <= 1e28:
                                body_size = 12
                                body_colour = (255, 110, 110)
                            else:
                                body_size = 16
                                body_colour = (255, 255, 200)
                            self.planets.append(Body(self.sim_x, 
                                                     self.sim_y, 
                                                     self.velocity_x,
                                                     self.velocity_y, 
                                                     self.next_mass, 
                                                     body_size, body_colour))
                            self.paused = False
                        elif not self.input_active:
                            self.start_position(event.pos)
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
                    elif self.paused:
                        self.update_velocity(event.pos)

            screen.fill((20, 20, 20))
            self.draw_grid()
            if not self.paused:
                for body in self.planets:
                    body.update_position(self.planets)
                    body.draw(self, screen, self.cam_x, self.cam_y)
                self.remove_offscreen_bodies()
                self.label_list_bodies()
            else:
                self.add_new_body()
                self.label_list_bodies()
            pygame.display.flip()
            clock.tick(60)
        pygame.quit()

def main():
    Simulation().run()

if __name__ == "__main__":
    main()
