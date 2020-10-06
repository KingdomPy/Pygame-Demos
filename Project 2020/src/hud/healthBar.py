import pygame


class HealthBar:

    def __init__(self, resolution, debug):
        self.resolution = resolution
        self.debug = debug

        self.x, self.y = self.resolution[0]*0.99, self.resolution[1]*0.01
        self.length = round(self.resolution[1] * 0.02)
        #  Every 150 points draw a cell
        self.cell_width = round(self.resolution[0] * 0.01)

        # Colours
        self.colour_filled = (38, 222, 73)  # (148, 55, 239)
        self.colour_filled_gradient = (33, 191, 63)  # (124, 51, 196)
        self.colour_background = (0, 0, 0)  # (34, 9, 62)
        self.colour_outline = (40, 40, 40)  # (200, 200, 200)
        self.outline_size = 1
    
    def draw_bar(self, surface, health, max_health):
        number_of_cells = (max_health - 1) // 150
        current_cell = max(int((health - 1) // 150), 0)
        cell_health = health - current_cell * 150

        if number_of_cells == current_cell:
            cell_max = max_health - number_of_cells * 150
            width = self.cell_width + self.resolution[0] * 0.14 * cell_max / 150
            border = pygame.Rect(self.x - width, self.y, width, self.length)
            percentage = width * cell_health / cell_max
            health_bar = pygame.Rect(self.x - percentage, self.y, percentage,
                                     self.length)
            health_bar_gradient = pygame.Rect(self.x - percentage, self.y + 0.6 * self.length,
                                              percentage, self.length *0.4)
            pygame.draw.rect(surface, self.colour_background, border)
            pygame.draw.rect(surface, self.colour_filled, health_bar)
            pygame.draw.rect(surface, self.colour_filled_gradient, health_bar_gradient)
            pygame.draw.rect(surface, self.colour_outline, border, self.outline_size)

        else:
            width = self.cell_width + self.resolution[0] * 0.14  # 0.14 * 1 = 0.14
            border = pygame.Rect(self.x - width, self.y, width, self.length)
            percentage = width * cell_health / 150
            health_bar = pygame.Rect(self.x - percentage, self.y,
                                     percentage, self.length)
            health_bar_gradient = pygame.Rect(self.x - percentage, self.y + 0.6 * self.length,
                                              percentage, self.length * 0.4)
            pygame.draw.rect(surface, self.colour_background, border)
            pygame.draw.rect(surface, self.colour_filled, health_bar)
            pygame.draw.rect(surface, self.colour_filled_gradient, health_bar_gradient)
            pygame.draw.rect(surface, self.colour_outline, border, self.outline_size)

        for i in range(number_of_cells):
            cell = pygame.Rect(self.x - self.cell_width*(i+1), self.y + self.length, self.cell_width, 3*self.length/4)
            if i >= current_cell:
                pygame.draw.rect(surface, self.colour_background, cell)
            else:
                cell_gradient = pygame.Rect(self.x - self.cell_width*(i+1), self.y + 1.45 * self.length,
                                                  self.cell_width, self.length * 0.3)
                pygame.draw.rect(surface, self.colour_filled, cell)
                pygame.draw.rect(surface, self.colour_filled_gradient, cell_gradient)
            pygame.draw.rect(surface, self.colour_outline, cell, self.outline_size)