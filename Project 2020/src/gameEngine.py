import math, json, pygame
from src import filePath, collision
from src.entities import baseEntity, player
from src.hud import healthBar, commandMenu, playerHud


class Engine:

    def __init__(self, resolution, fps, debug):
        self.resolution = resolution
        self.targetFps = fps
        self.debug = debug

        self.fpsScale = 16 * fps / 1000

        self.entities = []

        # Pointers used for the render order (reversed)
        self.entity_pointers = {
            "player": 0,
            "allies": 0,
            "enemies": 0,
            "projectiles": 0
        }

        self.camera = Camera(resolution, fps, debug)

        self.unit = 192  # 1 Meter = 192 pixels
        self.unit_scaled = 192 * (self.resolution[0] / 3200)  # 3200 x 1800 is the resolution the game is made for

        self.player = None

        self.mouse_touching = [-1, None]  # Distance to mouse, entity
        self.targeted_enemy = None  # Enemy that is currently being targeted or locked-on

        # Asset loading
        asset_path = filePath.setPath(filePath.getRootFolder(2), ["lib"])
        self.asset_scale = self.resolution[0] / 3200  # 3200 x 1800 is the resolution assets are created for

        # Fonts
        self.font_main = pygame.font.Font(filePath.setPath(asset_path, ["fonts", "Coda-Regular.ttf"]), 24)

        # Hud classes
        self.enemy_health_bar = healthBar.HealthBar(resolution, debug)
        self.command_menu = commandMenu.CommandMenu(resolution, debug)
        self.player_hud = playerHud.PlayerHud(resolution, debug)

        # Tile Map
        # Floor, Up, Down, Left, Right, TR, TL, BR, BL (Top Right... Bottom Left...)
        # 0,     1,    2,    3,    4,    5,  6,  7,  8
        self.tile_map_data = [
            6, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 5,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            3, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 4,
            8, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 7,
        ]

        self.camera.set_map(self.tile_map_data)

    def set_player_data(self, data):
        self.player.set_player_data(data)

    def add_entity(self, type, source=None, bullet_type=None):
        pointer = self.entity_pointers[type]

        if type == "projectiles":
            entity = baseEntity.Bullet(pointer, source, bullet_type)
            self.entity_pointers["enemies"] += 1
            self.entity_pointers["allies"] += 1
            self.entity_pointers["player"] += 1

        elif type == "enemies":
            entity = baseEntity.Entity(pointer)
            self.entity_pointers["allies"] += 1
            self.entity_pointers["player"] += 1

        elif type == "allies":
            entity = baseEntity.Entity(pointer)
            self.entity_pointers["player"] += 1

        else:
            entity = player.Player(pointer)
            self.player = entity
            self.camera.follow_entity(entity)

        entity.scale_entity(self.asset_scale)
        self.entities.insert(pointer, entity)
        return entity

    def remove_entity(self, index):
        pointer = self.entities[index].pointer
        self.entities.pop(index)

        if pointer == "projectiles":
            self.entity_pointers["enemies"] -= 1
            self.entity_pointers["allies"] -= 1
            self.entity_pointers["player"] -= 1

        elif pointer == "enemies":
            self.entity_pointers["allies"] -= 1
            self.entity_pointers["player"] -= 1

        elif pointer == "allies":
            self.entity_pointers["player"] -= 1

    def update(self, surface, events, dt, fps):
        dt /= 1000

        surface.fill((0, 0, 0))

        # Get input
        keys = pygame.key.get_pressed()

        x, y = pygame.mouse.get_pos()
        x = x - self.resolution[0]/2
        y = y - self.resolution[1]/2
        self.player.point_to(x + self.camera.x, y + self.camera.y)

        # Process input
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 1 - 5 = left, middle, right, scroll up, scroll down
                if event.button == 1:
                    action = self.player.left_mouse_pressed()
                    if action == "Surge" or action == "Hyper":
                        entity = self.add_entity("projectiles", self.player, action)

                    if action == "Spray":
                        for i in range(3):
                            entity = self.add_entity("projectiles", self.player, action)
                            entity.angle = self.player.angle + math.pi / 12 - i * math.pi / 12

                    elif action == "page up":
                        self.command_menu.page += 1
                        self.command_menu.selected = 0

                elif event.button == 3:
                    action = self.player.right_mouse_pressed()
                    if action == "page down":
                        self.command_menu.page -= 1
                        self.command_menu.selected = 0

                elif event.button == 4:
                    self.command_menu.selected = self.player.command_menu_scroll("up")

                elif event.button == 5:
                    self.command_menu.selected = self.player.command_menu_scroll("down")

            elif event.type == pygame.KEYDOWN:
                pass

        if keys[pygame.K_w]:
            self.player.move_forward(dt)

        if keys[pygame.K_i]:
            self.camera.change_zoom(1 * dt)

        if keys[pygame.K_o]:
            self.camera.change_zoom(-1 * dt)

        # Update entities
        camera_data = []
        entity_index = 0
        while entity_index < len(self.entities):
            entity = self.entities[entity_index]
            touching_mouse = (self.mouse_touching[1] is entity)  # Check if it was touching the mouse

            entity_status = entity.update(dt, touching_mouse)  # Update the entity

            if entity.entity_type == "bullet":  # Check for bullet collisions
                target_index = 0
                while target_index < len(self.entities):
                    target = self.entities[target_index]
                    if target is not entity.source and target.entity_type == "alive":
                        max_distance = entity.size + target.size
                        distance = math.sqrt((entity.x - target.x)**2 + (entity.y - target.y)**2)
                        if distance <= max_distance:
                            bulletPolygon, targetPolygon= entity.shape, target.shape
                            collided, pushValue = collision.polygonCollide(bulletPolygon, targetPolygon)
                            if collided:
                                entity_status = 0
                                target.receive_damage(35)
                                break
                    target_index += 1

            if entity_status == 1:
                in_camera = self.camera.in_camera((entity.x, entity.y), entity.current_size)

                if in_camera:
                    camera_data.append(entity.get_draw_data())

                    # Check if touching the mouse
                    if self.camera.following is not entity and entity.entity_type == "alive":  # Check baseEntity.py for the entity types
                        x_dif = (self.camera.x - entity.x) * self.camera.camera_zoom
                        y_dif = (self.camera.y - entity.y) * self.camera.camera_zoom
                        distance = math.sqrt((x_dif + x)**2 + (y_dif + y)**2)
                        # Get the distance from the mouse to the entity using the camera as the origin
                        if distance <= entity.size * self.camera.camera_zoom:
                            if self.mouse_touching[0] == -1 or distance < self.mouse_touching[0]:
                                self.mouse_touching = [distance, entity]
                                self.targeted_enemy = entity
                        else:
                            if touching_mouse:
                                self.mouse_touching = [-1, None]
                entity_index += 1

            else:
                if entity == self.targeted_enemy:
                    self.targeted_enemy = None
                    self.mouse_touching = [-1, None]
                    """distance = math.sqrt((self.camera.x + x - entity.x) ** 2 + (self.camera.y + y - entity.y) ** 2)
                    # Get the distance from the mouse to the entity using the camera as the origin
                    if distance > entity.size:
                        self.mouse_touching = [-1, None]"""
                self.remove_entity(entity_index)

        # Update the camera
        self.camera.update(dt)
        self.camera.update_screen(surface, camera_data)

        # Display HUD
        # Display hp of the enemy the that is currently being targeted
        if self.targeted_enemy is not None:
            self.enemy_health_bar.draw_bar(surface, self.targeted_enemy.health, self.targeted_enemy.max_health)

        # Display command menu
        self.command_menu.draw_menu(surface, self.player.command_menu)

        # Display the player hud
        self.player_hud.draw_hud(surface, self.player.health, self.player.max_health, self.player.energy, self.player.max_energy)

        if self.debug:
            text = self.font_main.render("FPS: " + str(fps), True, (255, 255, 255))
            surface.blit(text, (20, 20))


class Camera:

    def __init__(self, resolution, fps, debug):
        self.resolution = resolution
        self.targetFps = fps
        self.debug = debug

        self.fpsScale = 16 * fps / 1000

        self.center_x = resolution[0] / 2
        self.center_y = resolution[1] / 2

        self.following = None  # Assigned to an entity

        self.camera_speed = 170  # Speed it follows its target at
        self.max_distance = 100  # Furthest distance it can be from its target
        self.camera_zoom = 1  # Normal scaling

        self.x, self.y, self.angle = 0, 0, 0

        # Asset loading
        asset_path = filePath.setPath(filePath.getRootFolder(2), ["lib"])
        asset_scale = self.resolution[0] / 3200  # 3200 x 1800 is the resolution assets are created for

        self.assets_tiles = [pygame.image.load(filePath.setPath(asset_path, ["tiles", "floor.png"])).convert(),
                      pygame.image.load(filePath.setPath(asset_path, ["tiles", "up.png"])).convert(),
                      pygame.image.load(filePath.setPath(asset_path, ["tiles", "down.png"])).convert(),
                      pygame.image.load(filePath.setPath(asset_path, ["tiles", "left.png"])).convert(),
                      pygame.image.load(filePath.setPath(asset_path, ["tiles", "right.png"])).convert(),
                      pygame.image.load(filePath.setPath(asset_path, ["tiles", "top right.png"])).convert(),
                      pygame.image.load(filePath.setPath(asset_path, ["tiles", "top left.png"])).convert(),
                      pygame.image.load(filePath.setPath(asset_path, ["tiles", "bottom right.png"])).convert(),
                      pygame.image.load(filePath.setPath(asset_path, ["tiles", "bottom left.png"])).convert(),
                      pygame.image.load(filePath.setPath(asset_path, ["tiles", "panel.png"])).convert(),]

        self.tile_width = 192 * asset_scale
        self.tile_shift = self.tile_width / 2
        self.tile_map_data = None
        self.tile_map = []

        self.assets_sprites = [pygame.image.load(filePath.setPath(asset_path, ["player", "ship 1.png"])).convert_alpha(),
                        pygame.image.load(filePath.setPath(asset_path, ["bullets", "bullet.png"])).convert_alpha(),
                        pygame.image.load(filePath.setPath(asset_path, ["enemies", "crab.png"])).convert_alpha()]

        self.resize_assets()

    def resize_assets(self):
        asset_scale = self.resolution[0] / 3200  # 3200 x 1800 is the resolution assets are created for
        scale = asset_scale * self.camera_zoom

        x, y, width, length = self.assets_sprites[0].get_rect()
        self.player_sprite = pygame.transform.smoothscale(self.assets_sprites[0],
                                                          (round(width * scale), round(length * scale)))

        x, y, width, length = self.assets_sprites[1].get_rect()
        self.bullet_sprite = pygame.transform.smoothscale(self.assets_sprites[1],
                                                          (round(width * scale), round(length * scale)))

        x, y, width, length = self.assets_sprites[2].get_rect()
        self.crab_sprite = pygame.transform.smoothscale(self.assets_sprites[2],
                                                          (round(width * scale), round(length * scale)))

        self.tiles = []
        for tile in self.assets_tiles:
            x, y, width, length = tile.get_rect()
            tile = pygame.transform.smoothscale(tile, (round(width * scale), round(length * scale)))
            self.tiles.append(tile)

    def set_map(self, tile_map_data):
        self.tile_map_data = tile_map_data
        self.generate_map()

    def generate_map(self):
        size = int(math.sqrt(len(self.tile_map_data)))
        for i in range(size):
            for j in range(size):
                index = i * size + j
                tile_index = self.tile_map_data[index]
                position = (j * self.tile_width, i * self.tile_width)
                self.tile_map.append((position, tile_index))

    def follow_entity(self, target):
        self.following = target

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

    def move_forward(self, dt):
        self.x += math.cos(self.angle) * self.camera_speed * dt
        self.y += math.sin(self.angle) * self.camera_speed * dt

    def move_fixed(self, distance):
        self.x += math.cos(self.angle) * distance
        self.y += math.sin(self.angle) * distance

    def change_zoom(self, zoom):
        self.camera_zoom += zoom
        if self.camera_zoom > 2:
            self.camera_zoom = 2
        elif self.camera_zoom < 0.5:
            self.camera_zoom = 0.5
        self.resize_assets()

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
            distance = math.sqrt((self.x - target_x)**2 + (self.y - target_y)**2)
            step = distance / 64 * dt
            """if distance - step > 0:
                if distance - step > self.max_distance:
                    self.move_fixed(distance - self.max_distance)
                else:
                    self.move_forward(dt)
                    self.move_fixed(distance / 100)
            else:
                self.move_fixed(distance)"""
            if distance - step > 0:
                self.move_forward(step)
            else:
                self.move_fixed(distance)

    def update_screen(self, surface, images):  # Images are the entity shapes
        # Draw the tiles
        tiles = 0
        for tile in self.tile_map:
            position, index = tile
            image = self.tiles[index]
            if self.in_camera(position, self.tile_width / 2):
                screen_x = (position[0] - self.tile_shift - self.x) * self.camera_zoom + self.center_x
                screen_y = (position[1] - self.tile_shift - self.y) * self.camera_zoom + self.center_y
                surface.blit(image, (screen_x, screen_y))
                if self.debug:
                    tiles += 1
                    x, y, width, length = image.get_rect()
                    pygame.draw.rect(surface, (70, 70, 70), (screen_x, screen_y, width, length), 1)

        # Draw the entities
        for draw_data in images:
            new_image = []
            image_type, position, image, colour = draw_data
            x, y, angle = position

            if image_type == "player":
                image_surface = pygame.transform.rotozoom(self.player_sprite, 270 - angle * 180 / math.pi, 1)
                image_rect = image_surface.get_rect()
                x_dif = (self.x - x) * self.camera_zoom
                y_dif = (self.y - y) * self.camera_zoom
                image_rect.center = (self.center_x - x_dif, self.center_y - y_dif)
                surface.blit(image_surface, image_rect)

            elif image_type == "bullet":
                image_surface = pygame.transform.rotozoom(self.bullet_sprite, 270 - angle * 180 / math.pi, 1)
                image_rect = image_surface.get_rect()
                x_dif = (self.x - x) * self.camera_zoom
                y_dif = (self.y - y) * self.camera_zoom
                image_rect.center = (self.center_x - x_dif, self.center_y - y_dif)
                surface.blit(image_surface, image_rect)

            elif image_type == "crab":
                image_surface = pygame.transform.rotozoom(self.crab_sprite, 270 - angle * 180 / math.pi, 1)
                image_rect = image_surface.get_rect()
                x_dif = (self.x - x) * self.camera_zoom
                y_dif = (self.y - y) * self.camera_zoom
                image_rect.center = (self.center_x - x_dif, self.center_y - y_dif)
                surface.blit(image_surface, image_rect)

            if image_type == "polygon" or self.debug:
                for vertex in image:
                    screen_x = (vertex[0] - self.x) * self.camera_zoom + self.center_x
                    screen_y = (vertex[1] - self.y) * self.camera_zoom + self.center_y
                    new_image.append((screen_x, screen_y))
                pygame.draw.aalines(surface, colour, True, new_image)

