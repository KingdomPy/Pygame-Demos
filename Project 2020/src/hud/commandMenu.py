import pygame
from src import filePath


class CommandMenu:

    def __init__(self, resolution, debug):
        self.resolution = resolution
        self.debug = debug

        # Asset loading
        asset_path = filePath.setPath(filePath.getRootFolder(2), ["lib"])
        asset_scale = self.resolution[0] / 3200  # 3200 x 1800 is the resolution assets are created for

        # Fonts
        self.font_main = pygame.font.Font(filePath.setPath(asset_path, ["fonts", "TitilliumWeb-Regular.ttf"]), 26)

        # Hud images
        self.command_menu = [
            pygame.image.load(filePath.setPath(asset_path, ["player", "command menu", "commands.png"])).convert_alpha(),
            pygame.image.load(
                filePath.setPath(asset_path, ["player", "command menu", "slot_unselected.png"])).convert_alpha(),
            pygame.image.load(
                filePath.setPath(asset_path, ["player", "command menu", "slot_selected.png"])).convert_alpha(),
        ]

        # Scale images
        for i in range(len(self.command_menu)):  # Scale images
            x, y, width, length = self.command_menu[i].get_rect()
            self.command_menu[i] = pygame.transform.smoothscale(self.command_menu[i],
                                                          (round(width * asset_scale), round(length * asset_scale)))

        # Positions
        self.x = self.resolution[0]*0.01
        self.title_x = self.resolution[0]*0.02
        self.bottom = self.resolution[1]*0.97
        self.command_length = self.command_menu[1].get_rect()[3]
        self.title_length = self.command_menu[0].get_rect()[3]
        self.command_widths = [self.command_menu[1].get_rect()[2], self.command_menu[2].get_rect()[2]]

        self.selected = 0
        self.page = 0
        self.page_space = self.command_widths[0] / 10

    def draw_menu(self, surface, commands):
        for i in range(1, 6):
            slot = 1
            if i == 4 - self.selected and self.page == 0:
                slot = 2
            elif i == 5:
                slot = 0
                surface.blit(self.command_menu[slot], (self.title_x, self.bottom - self.command_length * 4 - self.title_length))
                break
            surface.blit(self.command_menu[slot], (self.x, self.bottom - self.command_length * i))

            if slot >= 1 and self.page == 0:
                if i == 4 - self.selected:
                    text = self.font_main.render(commands[4 - i], True, (255, 255, 255))
                else:
                    text = self.font_main.render(commands[4 - i], True, (200, 200, 200))
                text_rect = text.get_rect()
                text_rect.midleft = (self.title_x + self.page_space, self.bottom - self.command_length * i + self.command_length / 2)
                surface.blit(text, text_rect)

        if self.page > 0:
            for i in range(1, 5):
                slot = 1
                if i == 4 - self.selected and self.page == 1:
                    slot = 2
                surface.blit(self.command_menu[slot], (self.title_x + self.page * self.page_space/2, self.bottom - self.command_length * i - self.command_length * 0.2 * self.page))

                if self.page == 1 and 4 - i < len(commands):
                    if i == 4 - self.selected:
                        text = self.font_main.render(commands[4 - i], True, (255, 255, 255))
                    else:
                        text = self.font_main.render(commands[4 - i], True, (200, 200, 200))
                    text_rect = text.get_rect()
                    text_rect.midleft = (self.title_x + self.page * self.page_space * 2, self.bottom - self.command_length * i - self.command_length * 0.2 * self.page + self.command_length / 2)
                    surface.blit(text, text_rect)

    def new_draw(self, surface, commands):
        selected = 1
        for i in range(1, 6):
            is_selected = (i == 4 - self.selected) and self.page == 0
            if is_selected:
                selected = i
            elif i == 5:
                surface.blit(self.command_menu[0], (self.title_x, self.bottom - self.command_length * 4 - self.title_length))
            else:
                if i == 1:
                    surface.blit(self.command_menu[2], (self.x, self.bottom - self.command_length * i))
                else:
                    surface.blit(self.command_menu[1], (self.x, self.bottom - self.command_length * i))

            if self.page == 0 and i != 5:
                if not is_selected:
                    text = self.font_main.render(commands[4 - i], True, (180, 180, 180))
                    text_rect = text.get_rect()
                    text_rect.midleft = (self.x + self.page_space * 1.5, self.bottom - self.command_length * i + self.command_length / 2)
                    surface.blit(text, text_rect)

        if self.page == 0:
            surface.blit(self.command_menu[3], (self.x + self.page_space, self.bottom - self.command_length * selected))
            text = self.font_main.render(commands[4 - selected], True, (255, 255, 255))
            text_rect = text.get_rect()
            text_rect.midleft = (
            self.x + self.page_space * 2.5, self.bottom - self.command_length * selected + self.command_length / 2)
            surface.blit(text, text_rect)

        if self.page == 1:
            for i in range(1, 5):
                is_selected = (i == 4 - self.selected)
                if is_selected:
                    selected = i
                else:
                    if i == 1:
                        surface.blit(self.command_menu[2],
                                     (self.x + self.page_space * self.page,
                                      self.bottom - self.command_length * i - self.command_length * 0.2 * self.page))
                    else:
                        surface.blit(self.command_menu[1],
                                     (self.x + self.page_space * self.page,
                                      self.bottom - self.command_length * i - self.command_length * 0.2 * self.page))

                if 4 - i < len(commands):
                    if not is_selected:
                        text = self.font_main.render(commands[4 - i], True, (190, 190, 190))
                        text_rect = text.get_rect()
                        text_rect.midleft = (self.x + self.page_space * (self.page + 1.5),
                                             self.bottom - self.command_length * i - self.command_length * 0.2 * self.page + self.command_length / 2)
                        surface.blit(text, text_rect)

            surface.blit(self.command_menu[3],
                         (self.x + self.page_space * (self.page + 1),
                          self.bottom - self.command_length * selected - self.command_length * 0.2 * self.page))
            text = self.font_main.render(commands[4 - selected], True, (255, 255, 255))
            text_rect = text.get_rect()
            text_rect.midleft = (self.x + self.page_space * (self.page + 2.5),
                                 self.bottom - self.command_length * selected - self.command_length * 0.2 * self.page + self.command_length / 2)
            surface.blit(text, text_rect)
