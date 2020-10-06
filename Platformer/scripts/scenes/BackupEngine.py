import pygame
import math
import json
from tkinter import Tk
from tkinter import filedialog
from scripts import filePath
from scripts.entities import EntityController, TileController

asset_path = filePath.setPath(filePath.getRootFolder(2), ["assets"])

assets_tiles = [
    pygame.image.load(filePath.setPath(asset_path, ["maps", "grass.png"])).convert_alpha(),
    pygame.image.load(filePath.setPath(asset_path, ["maps", "rock.png"])).convert_alpha(),
    pygame.image.load(filePath.setPath(asset_path, ["maps", "background.png"])).convert_alpha(),
    pygame.image.load(filePath.setPath(asset_path, ["maps", "spawn.png"])).convert_alpha(),
    pygame.image.load(filePath.setPath(asset_path, ["maps", "goal.png"])).convert_alpha(),
]

assets_hud = [
    pygame.image.load(filePath.setPath(asset_path, ["map maker", "import.png"])).convert(),
    pygame.image.load(filePath.setPath(asset_path, ["map maker", "export.png"])).convert(),
]

assets_fonts = [
    filePath.setPath(asset_path, ["fonts", "Coda-Regular.ttf"]),
]


def collide_rect(rect1, rect2):
    x1, y1, w1, l1 = rect1
    x2, y2, w2, l2 = rect2

    x_collision = (x1 <= x2 <= x1 + w1) or (x1 <= x2 + w2 <= x1 + w1) or (x2 <= x1 <= x2 + w2) or (
                x2 <= x1 + w1 <= x2 + w2)
    y_collision = (y1 <= y2 <= y1 + l1) or (y1 <= y2 + l2 <= y1 + l1) or (y2 <= y1 <= y2 + l2) or (
                y2 <= y1 + l1 <= y2 + l2)

    if x_collision and y_collision:
        return True
    return False


class Scene:

    def __init__(self, resolution, fps, debug, data=None):
        self.resolution = resolution
        self.debug = debug

        self.resolution_scale = resolution[0] / 3200

        self.player = EntityController.Entity()
        self.player.scale_entity(self.resolution_scale)

        self.assistant = EntityController.Entity()
        self.assistant.scale_entity(self.resolution_scale)

        self.main_camera = Camera(resolution, debug)
        self.main_camera.following = self.player

        split_resolution = (resolution[0] / 2, resolution[1] / 2)

        self.split_camera_1 = Camera(split_resolution, debug)
        self.split_camera_1.change_zoom(self.split_camera_1.camera_zoom * 0.5)
        self.split_camera_1.following = self.player
        self.split_camera_2 = Camera(split_resolution, debug)
        self.split_camera_2.change_zoom(self.split_camera_2.camera_zoom * 0.5)
        self.split_camera_2.following = self.assistant

        self.half_surface_1 = pygame.Surface(split_resolution)
        self.half_surface_2 = pygame.Surface(split_resolution)

        self.display_mode = 0  # 0, 1 = single, split screen

        self.entities = [self.player, self.assistant]

        self.tile_size = 100  # width, length = 100
        self.chunk_size = 1200  # width, length = 1200
        self.tile_map = []
        self.spawn = (0, 0)
        self.goal = (0, 0)

        self.chunks = [[(0, 0)]]

        while not self.tile_map:
            self.import_tile_map()

        self.player.x = self.spawn[0]
        self.player.y = self.spawn[1] + self.player.length * 2

        self.assistant.x = self.spawn[0]
        self.assistant.y = self.spawn[1] + self.assistant.length * 2

        self.main_camera.tile_map = self.tile_map

        self.split_camera_1.tile_map = self.tile_map
        self.split_camera_2.tile_map = self.tile_map

        self.main_font = pygame.font.Font(assets_fonts[0], int(16 + 8 * self.resolution_scale))

    def resize_assets(self):
        self.main_font = pygame.font.Font(assets_fonts[0], int(16 + 8 * self.resolution_scale))

    def import_tile_map(self):
        root = Tk()
        root.withdraw()

        path = filedialog.askopenfilename(filetypes=(("Text Files", ".json .txt"),))
        if path != "":
            with open(path, 'r', encoding='utf-8-sig') as file:
                data = json.loads(file.read())
                tile_map = data["tile_map"]

            scale = self.resolution[0] / 3200

            for x, y, sprite_code in tile_map:
                x -= self.tile_size * scale
                tile = TileController.Tile(self.tile_size, self.tile_size, sprite_code)
                tile.x, tile.y = x, y

                if sprite_code == 2:
                    tile.collidable = False
                elif sprite_code == 3:
                    tile.collidable = False
                    tile.visible = False
                    self.spawn = (x, y)
                elif sprite_code == 4:
                    self.goal = (x, y)

                chunk_x = x // self.chunk_size
                chunk_y = y // self.chunk_size
                for i in range(len(self.chunks)):
                    chunk = self.chunks[i]
                    if chunk[0] == (chunk_x, chunk_y):
                        chunk.append(tile)
                    elif i == len(self.chunks) - 1:
                        self.chunks.append([(chunk_x, chunk_y), tile])
                        break
                self.tile_map.append(tile)

        print(self.chunks)
        root.destroy()

    def update(self, surface, events, dt, current_fps):
        dt /= 1000

        if self.display_mode == 0:
            surface.fill((255, 255, 255))
        elif self.display_mode == 1:
            self.half_surface_1.fill((255, 255, 255))
            self.half_surface_2.fill((255, 255, 255))

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.player.w_pressed = True

        if keys[pygame.K_a]:
            self.player.a_pressed = True

        if keys[pygame.K_d]:
            self.player.d_pressed = True

        if keys[pygame.K_UP]:
            self.assistant.w_pressed = True

        if keys[pygame.K_LEFT]:
            self.assistant.a_pressed = True

        if keys[pygame.K_RIGHT]:
            self.assistant.d_pressed = True

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "switch", "map creator", []

                if event.key == pygame.K_SPACE:
                    self.display_mode += 1
                    self.display_mode %= 2

        camera_data = []

        split_camera_1_data = []
        split_camera_2_data = []

        for entity in self.entities:
            entity.update(dt)

            my_rect = entity.get_rect()
            for tile in self.tile_map:
                if tile.collidable:
                    distance = math.sqrt(
                        (entity.x - tile.x) ** 2 + (entity.y - tile.y) ** 2) - entity.width - tile.width
                    if tile.angle == 0 and entity.angle == 0 and distance <= 0:
                        tile_rect = tile.get_rect()
                        if collide_rect(my_rect, tile_rect):
                            if tile.sprite_code == 4:
                                self.player.x = self.spawn[0]
                                self.player.y = self.spawn[1] + self.player.length * 2
                            else:
                                x_overlap = min(abs((tile.x + tile.width / 2) - (entity.x - entity.width / 2)),
                                                abs((entity.x + entity.width / 2) - (tile.x - tile.width / 2)))
                                y_overlap = min(abs((tile.y + tile.length / 2) - (entity.y - entity.length / 2)),
                                                abs((entity.y + entity.length / 2) - (tile.y - tile.length / 2)))

                                if abs(x_overlap) < abs(y_overlap):  # Shift the x
                                    if entity.x < tile.x:
                                        entity.touching_right_wall = True
                                        entity.x -= x_overlap
                                    else:
                                        entity.touching_left_wall = True
                                        entity.x += x_overlap

                                else:  # Shift the y
                                    if entity.y < tile.y:
                                        entity.touching_ceiling = True
                                        entity.fall_velocity = 0
                                        entity.y -= y_overlap
                                    else:
                                        entity.touching_ground = True
                                        entity.y += y_overlap

                            my_rect = entity.get_rect()

            position, radius = entity.get_position(), entity.width / 2
            if self.display_mode == 0:
                if self.main_camera.in_camera(position, radius):
                    camera_data.append(entity.get_polygon())

            elif self.display_mode == 1:
                if self.split_camera_1.in_camera(position, radius):
                    split_camera_1_data.append(entity.get_polygon())
                if self.split_camera_2.in_camera(position, radius):
                    split_camera_2_data.append(entity.get_polygon())

        if self.display_mode == 0:
            self.main_camera.update(dt)
            self.main_camera.update_screen(surface, camera_data)

            text = self.main_font.render("FPS:" + str(current_fps), True, (0, 0, 0))
            surface.blit(text, (10, 10))
        elif self.display_mode == 1:
            self.split_camera_1.update(dt)
            self.split_camera_1.update_screen(self.half_surface_1, split_camera_1_data)
            surface.blit(self.half_surface_1, (self.resolution[0] / 4, 0))
            self.split_camera_2.update(dt)
            self.split_camera_2.update_screen(self.half_surface_2, split_camera_2_data)
            surface.blit(self.half_surface_2, (self.resolution[0] / 4, self.resolution[1] / 2))

            text = self.main_font.render("FPS:" + str(current_fps), True, (0, 0, 0))
            surface.blit(text, (self.resolution[0] / 4 + 10, 10))

        return 0


class Camera:

    def __init__(self, resolution, debug):
        self.resolution = resolution

        self.center_x = resolution[0] / 2
        self.center_y = resolution[1] / 2

        self.debug = debug

        self.camera_speed = 270
        self.camera_zoom = 1 * resolution[0] / 3200
        self.max_zoom = 8 * resolution[0] / 3200
        self.min_zoom = 0.1 * resolution[0] / 3200
        self.following = None

        self.x, self.y, self.angle = 0, 0, 0

        self.tile_map_name = "Untitled"
        self.tile_map = []
        self.tiles = []
        self.display_tiles = []
        self.display_assets = []

        self.tile_size = 100
        self.display_size = self.tile_size * 2 / 3

        self.resize_assets()

    def resize_assets(self):
        scale = round(self.display_size)
        self.display_tiles = []
        for tile in assets_tiles:
            tile = pygame.transform.smoothscale(tile, (scale, scale))
            self.display_tiles.append(tile)
        for asset in assets_hud:
            asset = pygame.transform.smoothscale(asset, (scale, scale))
            self.display_assets.append(asset)
        self.resize_tiles()

    def resize_tiles(self):
        scale = round(self.tile_size * self.camera_zoom)
        self.tiles = []
        for tile in assets_tiles:
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

    def update_screen(self, surface, camera_data):
        for tile in self.tile_map:
            if tile.visible:
                if self.in_camera(tile.get_position(), tile.width / 2):
                    image = self.tiles[tile.sprite_code]
                    width = tile.width * self.camera_zoom
                    length = tile.length * self.camera_zoom
                    screen_x = self.center_x - (self.x - tile.x) * self.camera_zoom
                    screen_y = self.center_y + (self.y - tile.y) * self.camera_zoom
                    surface.blit(image, (screen_x - width / 2, screen_y - length / 2))
                    if self.debug:
                        pygame.draw.rect(surface, (0, 0, 0),
                                         (screen_x - width / 2, screen_y - length / 2, width, length), 5)

        for polygon in camera_data:
            points = []
            for x, y in polygon:
                screen_x = self.center_x - (self.x - x) * self.camera_zoom
                screen_y = self.center_y + (self.y - y) * self.camera_zoom
                points.append((screen_x, screen_y))
            pygame.draw.polygon(surface, (0, 0, 0), points)


