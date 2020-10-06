import pygame
import math

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

        self.player = EntityController.Entity()

        self.player.x += 100
        self.player.y += self.player.length / 2

        self.camera = Camera(debug)

        self.camera.following = self.player

        self.entities = [self.player]

        tile_map_data = []

        tile_map_data = [
            1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1,
            2, 0, 0, 0, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2,
            2, 0, 0, 0, 0, 0, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2,
            2, 1, 1, 1, 0, 0, 2, 2, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 2,
            2, 2, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2,
            2, 2, 2, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2,
            2, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2,
            2, 0, 0, 2, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 0, 2, 0, 0, 0, 0, 2,
            2, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2,
            2, 0, 0, 2, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2,
            2, 0, 0, 2, 0, 0, 2, 2, 1, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 2,
            2, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2,
            2, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2,
            2, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 2,
            2, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 2, 2, 0, 0, 0, 0, 0, 0, 0, 2,
            2, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2,
            2, 0, 0, 2, 0, 0, 2, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2,
            2, 0, 0, 2, 0, 0, 2, 2, 1, 0, 0, 2, 2, 2, 0, 0, 0, 0, 0, 0, 2,
            2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 2,
            2, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2,
            2, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
        ]

        width, length = 21, 21

        for i in range(len(tile_map_data)):
            sprite_code = tile_map_data[i]
            tile = TileController.Tile(50, 50, tile_map_data[i] - 1)
            tile_map_data[i] = tile
            if sprite_code == 0:
                tile.collidable = False

        self.tile_map = self.camera.generate_map(tile_map_data, width, length)

        self.draw_buffer = pygame.Surface((3200, 1600))

    def update(self, surface, events, dt, current_fps):
        dt /= 1000

        self.draw_buffer.fill((255, 255, 255))

        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.player.w_pressed = True

        if keys[pygame.K_a]:
            self.player.a_pressed = True

        if keys[pygame.K_d]:
            self.player.d_pressed = True

        camera_data = []

        for entity in self.entities:
            entity.update(dt)
            position = entity.get_position()

            position, radius = entity.get_position(), entity.width / 2

            if self.camera.in_camera(position, radius):
                my_rect = entity.get_rect()
                for tile in self.tile_map:
                    if tile.collidable:
                        if tile.angle == 0 and entity.angle == 0:
                            tile_rect = tile.get_rect()
                            if collide_rect(my_rect, tile_rect):

                                x_overlap = min(abs((tile.x + tile.width / 2) - (entity.x - entity.width / 2)),
                                                abs((entity.x + entity.width / 2) - (tile.x - tile.width / 2)))
                                y_overlap = min(abs((tile.y + tile.length / 2) - (entity.y - entity.length / 2)),
                                                abs((entity.y + entity.length / 2) - (tile.y - tile.length / 2)))

                                """if entity.y > tile.y + tile.length / 2:
                                    entity.y = tile.y + tile.length
                                else:
                                    entity.y = tile.y - tile.length"""

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

                camera_data.append(entity.get_polygon())

        self.camera.update(dt)
        self.camera.update_screen(self.draw_buffer, camera_data)
        surface.blit(pygame.transform.scale(self.draw_buffer, self.resolution), (0, 0))
        return 0


class Camera:

    def __init__(self, debug):
        self.debug = debug

        self.camera_speed = 270
        self.camera_zoom = 2.5
        self.following = None

        self.x, self.y, self.angle = 0, 0, 0

        self.center_x = 1600
        self.center_y = 900

        self.tile_map_data = None
        self.tile_map = []
        self.tiles = []

        asset_path = filePath.setPath(filePath.getRootFolder(2), ["assets"])

        self.assets_tiles = [
            pygame.image.load(filePath.setPath(asset_path, ["maps", "grass.png"])).convert(),
            pygame.image.load(filePath.setPath(asset_path, ["maps", "rock.png"])).convert(),
            pygame.image.load(filePath.setPath(asset_path, ["maps", "background.png"])).convert(),
        ]

        self.resize_assets()

    def resize_assets(self):
        scale = 50 * self.camera_zoom
        self.tiles = []
        for tile in self.assets_tiles:
            x, y, width, length = tile.get_rect()
            tile = pygame.transform.smoothscale(tile, (round(scale), round(scale)))
            self.tiles.append(tile)

    def generate_map(self, tile_map_data, width, length):
        size = round(math.sqrt(len(tile_map_data)))
        for i in range(length):
            for j in range(width):
                tile = tile_map_data[i * width + j]
                tile.x, tile.y = j * tile.width, -1 * i * tile.length
                self.tile_map.append(tile)
        return self.tile_map

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
            if self.in_camera(tile.get_position(), tile.width / 2):
                image = self.tiles[tile.sprite_code]
                width = tile.width * self.camera_zoom
                length = tile.length * self.camera_zoom
                screen_x = self.center_x - (self.x - tile.x) * self.camera_zoom
                screen_y = self.center_y + (self.y - tile.y) * self.camera_zoom
                surface.blit(image, (screen_x - width / 2, screen_y - length / 2))
                if self.debug:
                    pygame.draw.rect(surface, (0, 0, 0), (screen_x - width / 2, screen_y - length / 2, width, length), 5)

        for polygon in camera_data:
            points = []
            for x, y in polygon:
                screen_x = self.center_x - (self.x - x) * self.camera_zoom
                screen_y = self.center_y + (self.y - y) * self.camera_zoom
                points.append((screen_x, screen_y))
            pygame.draw.polygon(surface, (0, 0, 0), points)


