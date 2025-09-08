#import numpy as np
import pygame
import math

pygame.init()
WIDTH, HEIGHT = 1500, 1000
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gravitational Simulation")
clock = pygame.time.Clock()

G = 6.67430e-11  # Gravitational constant
TIME_STEP = 86400  # Time step for simulation
ZOOM_SCALE = 6e-11  # Zoom scale for visualization
SCALE = 1e-9  # Scale to convert simulation units to screen units
ZOOMED = False

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
                if distance > 0:
                    force = (G * self.mass * body.mass) / (distance*distance)
                    fx += force * dx / distance
                    fy += force * dy / distance
        ax = (fx)/ self.mass
        ay = (fy)/ self.mass
        self.vx += ax * TIME_STEP
        self.vy += ay * TIME_STEP
        self.x += self.vx * TIME_STEP
        self.y += self.vy * TIME_STEP

        current_scale = ZOOM_SCALE if ZOOMED else SCALE

        self.trail.append((int(self.x * current_scale + WIDTH // 2), int(self.y * current_scale + HEIGHT // 2)))
        if len(self.trail) > 20000:
            self.trail.pop(0)
    
    def draw(self, screen):
        if len(self.trail) > 1:
            pygame.draw.lines(screen, (50, 50, 50), False, self.trail, 1)
        
        current_scale = ZOOM_SCALE if ZOOMED else SCALE
        screen_x = int(self.x * current_scale + WIDTH // 2)
        screen_y = int(self.y * current_scale + HEIGHT // 2)

        pygame.draw.circle(screen, self.color, (screen_x, screen_y), self.radius)

bodies = [
    Body(0, 0, 0, 0, 1.989e30, 4, (255, 255, 0)),  # Sun  (1.989e30 kg, 8 pixel radius (not used in calculations, just visual))
    Body(5.79e10, 0, 0, 47360, 3.301e23, 2, (255, 30, 150)),  # Mercury
    Body(1.082e11, 0, 0, 35020, 4.867e24, 2, (255, 30, 150)),  # Venus
    Body(1.496e11, 0, 0, 29780, 5.972e24, 4, (0, 100, 255)),  # Earth
    Body(279e11, 0, 0, 24077, 6.39e23, 3, (255, 30, 150)),  # Mars
    Body(7.786e11, 0, 0, 13070, 1.898e27, 2, (255, 30, 150)),  # Jupiter
    Body(1.432e12, 0, 0, 9680, 5.683e26, 2, (255, 30, 150)),  # Saturn
    Body(2.867e12, 0, 0, 6810, 8.681e25, 2, (255, 30, 150)),  # Uranus
    Body(4.515e12, 0, 0, 5430, 1.024e26, 2, (255, 30, 150)),  # Neptune
    Body(5.906e12, 0, 0, 4670, 1.309e22, 2, (255, 30, 150))  # Pluto
]

running=True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                ZOOMED = not ZOOMED
            for body in bodies:
                body.trail = []

    screen.fill((0, 0, 0))

    for body in bodies:
        body.update_position(bodies)
        body.draw(screen)

    pygame.display.flip()
    clock.tick(60)
pygame.quit()