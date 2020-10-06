import pygame


class PlayerHud:

    def __init__(self, resolution, debug):
        self.resolution = resolution
        self.debug = debug

        self.health_frame = pygame.Rect(0, 0, self.resolution[0]*0.2, self.resolution[1]*0.035)
        self.health_fill = pygame.Rect(0, 0, self.resolution[0] * 0.2, self.resolution[1] * 0.035)
        self.health_fill_gradient = pygame.Rect(0, 0, self.resolution[0] * 0.2, self.resolution[1] * 0.014)
        self.health_frame.bottomright = (self.resolution[0] * 0.99, self.resolution[1] * 0.95)

        self.energy_frame = pygame.Rect(0, 0, self.resolution[0] * 0.15, self.resolution[1] * 0.02)
        self.energy_fill = pygame.Rect(0, 0, self.resolution[0] * 0.15, self.resolution[1] * 0.02)
        self.energy_fill_gradient = pygame.Rect(0, 0, self.resolution[0] * 0.15, self.resolution[1] * 0.008)
        self.energy_frame.bottomright = (self.resolution[0] * 0.99, self.resolution[1] * 0.97)

        # Colours
        self.health_filled = (38, 222, 73)  # (37, 199, 34)
        self.health_filled_gradient = (33, 191, 63)  # (32, 173, 29)

        self.energy_filled = (232, 224, 67)  # (39, 159, 207)
        self.energy_filled_gradient = (209, 202, 59)  # (32, 142, 186)

        self.energy_filling = (199, 65, 217)
        self.energy_filling_gradient = (159, 50, 173)

        self.border = (40, 40, 40)  # (200, 200, 200)
        self.border_outline = 1

    def draw_hud(self, surface, health, max_health, energy, max_energy):
        # Health bar
        pygame.draw.rect(surface, (0, 0, 0), self.health_frame)

        self.health_fill.width = self.health_frame.width * health / max_health
        self.health_fill_gradient.width = self.health_fill.width

        self.health_fill.bottomright = (self.resolution[0] * 0.99, self.resolution[1] * 0.95)
        self.health_fill_gradient.bottomright = self.health_fill.bottomright

        pygame.draw.rect(surface, self.health_filled, self.health_fill)
        pygame.draw.rect(surface, self.health_filled_gradient, self.health_fill_gradient)
        pygame.draw.rect(surface, self.border, self.health_frame, self.border_outline)

        # Energy bar
        pygame.draw.rect(surface, (0, 0, 0), self.energy_frame)

        self.energy_fill.width = abs(self.energy_frame.width * energy / max_energy)
        self.energy_fill_gradient.width = self.energy_fill.width

        self.energy_fill.bottomright = (self.resolution[0] * 0.99, self.resolution[1] * 0.97)
        self.energy_fill_gradient.bottomright = self.energy_fill.bottomright

        if energy > 0:
            pygame.draw.rect(surface, self.energy_filled, self.energy_fill)
            pygame.draw.rect(surface, self.energy_filled_gradient, self.energy_fill_gradient)
        else:
            pygame.draw.rect(surface, self.energy_filling, self.energy_fill)
            pygame.draw.rect(surface, self.energy_filling_gradient, self.energy_fill_gradient)
        pygame.draw.rect(surface, self.border, self.energy_frame, self.border_outline)

