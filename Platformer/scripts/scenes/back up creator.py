import pygame
import math
import json
from tkinter import Tk
from tkinter import filedialog
from scripts import filePath
from scripts.entities import EntityController, TileController


def collide_rect(rect1, rect2):
    x1, y1, w1, l1 = rect1
    x2, y2, w2, l2 = rect2

    x_collision = (x1 <= x2 <= x1+w1) or (x1 <= x2+w2 <= x1+w1) or (x2 <= x1 <= x2+w2) or (x2 <= x1+w1<= x2+w2)
    y_collision = (y1 <= y2 <= y1+l1) or (y1 <= y2+l2 <= y1+l1) or (y2 <= y1 <= y2+l2) or (y2 <= y1+l1 <= y2+l2)

    if x_collision and y_collision:
        return True
    return False


class Scene:

    def __init__(self, resolution, fps, debug, data=None):
        self.resolution = resolution

        self.debug = debug

        self.center_x = resolution[0] / 2
        self.center_y = resolution[1] / 2

        self.player = EntityController.Entity()

        self.player.x += 100
        self.player.y += self.player.length / 2

        self.camera = Camera(resolution, debug)

        self.tile_size = 200 * resolution[0] / 3200

        self.tile_slots = {}  # Position, index in tile map

        self.selected_tile = 0

        # left x, top y, right x, bottom y
        self.collisions = [
            (self.resolution[0] * 0.99 - self.camera.display_size * 2 - 10, 10,
             self.resolution[0] * 0.99 - self.camera.display_size * 2 - 10 + self.camera.display_size,
             self.camera.display_size + 10),
            (self.resolution[0] * 0.99 - self.camera.display_size, 10, self.resolution[0] * 0.99,
             self.camera.display_size + 10)
        ]

        self.collision_names = ["import", "export"]

    def import_tile_map(self):
        root = Tk()
        root.withdraw()

        path = filedialog.askopenfilename(filetypes=(("Text Files", ".json .txt"), ))
        if path != "":
            with open(path, 'r', encoding='utf-8-sig') as file:
                data = json.loads(file.read())
                tile_map = data["tile_map"]

            self.tile_slots = {}
            self.camera.tile_map = []

            for x, y, sprite_code in tile_map:
                x -= self.tile_size / 2
                y -= self.tile_size / 2
                tile = TileController.Tile(self.tile_size, self.tile_size, sprite_code)
                tile.x, tile.y = x, y
                if sprite_code == 3:
                    self.camera.x, self.camera.y = x, y
                self.camera.tile_map.append(tile)
                self.tile_slots[(x, y)] = tile
        root.destroy()

    def export_tile_map(self):
        root = Tk()
        root.withdraw()

        export = []
        tile_map = []
        min_x = 1000000
        max_y = -1000000
        for tile in self.camera.tile_map:
            if tile.x < min_x:
                min_x = tile.x
            if tile.y > max_y:
                max_y = tile.y
            tile_map.append((tile.x, tile.y, tile.sprite_code))
        for x, y, sprite_code in tile_map:
            x -= min_x
            y -= max_y
            export.append((x, y, sprite_code))
        export = {'map_name': self.camera.tile_map_name, 'tile_map': export}
        path = filedialog.asksaveasfilename(filetypes=(("Text Files", ".json .txt"), ))
        if path != "":
            with open(path, 'w', encoding='utf-8-sig') as file:
                file.write(json.dumps(export))
                file.close()
        root.destroy()

    def update(self, surface, events, dt, current_fps):
        dt /= 1000

        surface.fill((255, 255, 255))

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.camera.y += self.camera.camera_speed * dt / self.camera.camera_zoom

        if keys[pygame.K_s]:
            self.camera.y -= self.camera.camera_speed * dt / self.camera.camera_zoom

        if keys[pygame.K_a]:
            self.camera.x -= self.camera.camera_speed * dt / self.camera.camera_zoom

        if keys[pygame.K_d]:
            self.camera.x += self.camera.camera_speed * dt / self.camera.camera_zoom

        if keys[pygame.K_i]:
            self.camera.change_zoom(3 * dt)

        if keys[pygame.K_o]:
            self.camera.change_zoom(-3 * dt)

        x, y = pygame.mouse.get_pos()
        mouse_pressed = pygame.mouse.get_pressed()

        can_place = True
        for i in range(len(self.collisions)):
            box = self.collisions[i]
            if box[0] <= x <= box[2] and box[1] <= y <= box[3]:
                can_place = self.collision_names[i]
                break

        x = (x - self.center_x) / self.camera.camera_zoom + self.camera.x
        y = (self.center_y - y) / self.camera.camera_zoom + self.camera.y
        x = self.tile_size * (x // self.tile_size)
        y = self.tile_size * (y // self.tile_size)

        x += self.tile_size / 2
        y += self.tile_size / 2

        mouse_x, mouse_y = x, y

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self.selected_tile = 0
                if event.key == pygame.K_2:
                    self.selected_tile = 1
                if event.key == pygame.K_3:
                    self.selected_tile = 2
                if event.key == pygame.K_4:
                    self.selected_tile = 3
                if event.key == pygame.K_5:
                    self.selected_tile = 4

                if event.key == pygame.K_ESCAPE:
                    return "switch", "test", []

        if mouse_pressed[0]:
            if can_place is True:
                if (x, y) not in self.tile_slots:
                    if self.debug:
                        print("place:", x, y)
                    tile = TileController.Tile(self.tile_size, self.tile_size, self.selected_tile)
                    tile.x, tile.y = x, y
                    self.camera.tile_map.append(tile)
                    self.tile_slots[(x, y)] = tile

            elif can_place == "import":
                self.import_tile_map()

            elif can_place == "export":
                self.export_tile_map()

        if mouse_pressed[2]:
            if (x, y) in self.tile_slots:
                if self.debug:
                    print("delete:", x, y)
                tile = self.tile_slots[(x, y)]
                self.camera.tile_map.remove(tile)
                del self.tile_slots[(x, y)]

        self.camera.update_screen(surface, (mouse_x, mouse_y), self.selected_tile)
        return 0


class Camera:

    def __init__(self, resolution, debug):
        self.resolution = resolution

        self.center_x = resolution[0] / 2
        self.center_y = resolution[1] / 2

        self.debug = debug

        self.camera_speed = 500
        self.camera_zoom = 1
        self.max_zoom = 8
        self.min_zoom = 0.1
        self.following = None

        self.x, self.y, self.angle = 0, 0, 0

        self.tile_map_name = "Untitled"
        self.tile_map = []
        self.tiles = []
        self.display_tiles = []
        self.display_assets = []

        asset_path = filePath.setPath(filePath.getRootFolder(2), ["assets"])

        self.assets_tiles = [
            pygame.image.load(filePath.setPath(asset_path, ["maps", "grass.png"])).convert_alpha(),
            pygame.image.load(filePath.setPath(asset_path, ["maps", "rock.png"])).convert_alpha(),
            pygame.image.load(filePath.setPath(asset_path, ["maps", "background.png"])).convert_alpha(),
            pygame.image.load(filePath.setPath(asset_path, ["maps", "spawn.png"])).convert_alpha(),
            pygame.image.load(filePath.setPath(asset_path, ["maps", "goal.png"])).convert_alpha(),
        ]

        self.assets_hud = [
            pygame.image.load(filePath.setPath(asset_path, ["map maker", "import.png"])).convert(),
            pygame.image.load(filePath.setPath(asset_path, ["map maker", "export.png"])).convert(),
        ]

        self.tile_size = 200 * resolution[0] / 3200
        self.display_size = self.tile_size * 2/3

        self.resize_assets()

    def resize_assets(self):
        scale = round(self.display_size)
        self.display_tiles = []
        for tile in self.assets_tiles:
            tile = pygame.transform.smoothscale(tile, (scale, scale))
            self.display_tiles.append(tile)
        for asset in self.assets_hud:
            asset = pygame.transform.smoothscale(asset, (scale, scale))
            self.display_assets.append(asset)
        self.resize_tiles()

    def resize_tiles(self):
        scale = round(self.tile_size * self.camera_zoom)
        self.tiles = []
        for tile in self.assets_tiles:
            tile = pygame.transform.smoothscale(tile, (scale, scale))
            self.tiles.append(tile)

    def move_forward(self, dt):
        self.x += math.cos(self.angle) * self.camera_speed * dt
        self.y += math.sin(self.angle) * self.camera_speed * dt

    def move_fixed(self, distance):
        self.x += math.cos(self.angle) * distance
        self.y += math.sin(self.angle) * distance

    def point_in_direction(self, x_dif, y_dif):
        if y_dif < 0:
            self.angle = - math.pi / 2 - math.atan(x_dif / y_dif)
        else:
            if y_dif != 0:
                self.angle = math.pi / 2 - math.atan(x_dif / y_dif)
            elif y_dif == 0:
                if x_dif < 0:
                    self.angle = -math.pi
                else:
                    self.angle = math.pi

    def point_to(self, x, y):
        self.point_in_direction(x - self.x, y - self.y)

    def in_camera(self, position, radius):
        x_dif = abs(self.x - position[0])
        y_dif = abs(self.y - position[1])
        if x_dif - radius < self.center_x / self.camera_zoom and y_dif - radius < self.center_y / self.camera_zoom:
            return 1
        return 0

    def change_zoom(self, zoom):
        self.camera_zoom += zoom
        if self.camera_zoom > self.max_zoom:
            self.camera_zoom = self.max_zoom
        elif self.camera_zoom < self.min_zoom:
            self.camera_zoom = self.min_zoom
        self.resize_tiles()

    def update(self, dt):
        if self.following is not None:
            target_x, target_y = self.following.get_position()
        self.point_to(target_x, target_y)
        distance = math.sqrt((self.x - target_x) ** 2 + (self.y - target_y) ** 2)
        step = distance / 64 * dt
        if distance - step > 0:
            self.move_forward(step)
        else:
            self.move_fixed(distance)

    def update_screen(self, surface, mouse, selected_tile):
        outline = round(min(max(1, 5 * self.camera_zoom), 5))
        for tile in self.tile_map:
            if self.in_camera(tile.get_position(), tile.width / 2):
                image = self.tiles[tile.sprite_code]
                width = tile.width * self.camera_zoom
                length = tile.length * self.camera_zoom
                screen_x = self.center_x - (self.x - tile.x) * self.camera_zoom
                screen_y = self.center_y + (self.y - tile.y) * self.camera_zoom
                surface.blit(image, (screen_x - width / 2, screen_y - length / 2))
                if self.debug:
                    pygame.draw.rect(surface, (0, 0, 0), (screen_x - width / 2, screen_y - length / 2, width, length), outline)

        x, y = mouse
        screen_x = self.center_x - (self.x - x) * self.camera_zoom
        screen_y = self.center_y + (self.y - y) * self.camera_zoom
        image = self.tiles[selected_tile].copy()
        image.fill((255, 255, 255, 120), None, pygame.BLEND_RGBA_MULT)
        width = self.tile_size * self.camera_zoom
        surface.blit(image, (screen_x - width / 2, screen_y - width / 2))

        # Draw Hud
        for i in range(len(self.display_tiles)):
            tile = self.display_tiles[i]
            x = 10 + i * (self.display_size + 10)
            y = 10
            surface.blit(tile, (x, y))
            if i == selected_tile:
                pygame.draw.rect(surface, (200, 200, 100), (x, y, self.display_size, self.display_size), 4)

        image = self.display_assets[0]
        surface.blit(image, (self.resolution[0] * 0.99 - self.display_size * 2 - 10, y))
        image = self.display_assets[1]
        surface.blit(image, (self.resolution[0] * 0.99 - self.display_size, y))

        y += self.display_size + 10
        pygame.draw.line(surface, (0, 0, 0), (0, y), (self.resolution[0], y), 4)

