import math
from src import contentLoader

projectile_data = contentLoader.load_projectile_data()


class Entity:

    def __init__(self, pointer):
        # Attributes
        self.entity_type = "alive"  # alive, bullet, dead
        self.pointer = pointer  # player, allies, enemies, projectiles

        # alive = Has an AI, can move, has health, can not be interacted with
        # bullet = Is a projectile, has no health, can not be interacted with
        # dead = Has no AI, can not move, can only be interacted with

        # Position
        self.x, self.y, self.angle = 0, 0, math.pi/4  # Angle is in radians

        # Default Display
        self.mapping = ((1, 0), (1, math.pi/2), (1, math.pi), (1, -math.pi/2))  # (radius, angle in radians)
        self.size = 134  # Scale factor for mapping
        self.colour = (0, 0, 0)
        self.name = "Entity"
        self.sprite_type = "crab"

        # Animations
        self.shape = []  # List of xy coordinates for each vertex of the entity
        self.current_size = self.size
        self.set_size(self.size)
        self.current_colour = self.colour

        # Stats
        self.movement_speed = 200
        self.health = 1500
        self.max_health = 1500
        self.energy = 20

    def scale_entity(self, entity_scale):
        self.size *= entity_scale
        self.current_size = self.size
        self.movement_speed *= entity_scale
        self.set_size(self.size)

    def scale_position(self, entity_scale):
        x = entity_scale * self.x
        y = entity_scale * self.y
        self.shift_shape(-x, -y)

    def get_draw_data(self):
        return self.sprite_type, (self.x, self.y, self.angle), self.shape, self.current_colour

    def get_position(self):
        return self.x, self.y

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.set_size(self.current_size)

    def set_size(self, size):
        self.shape = []
        self.current_size = size
        for i in self.mapping:
            radius, angle = i
            point = ((size * radius * math.cos(angle + self.angle) + self.x), (size * radius * math.sin(angle + self.angle) + self.y))
            self.shape.append(point)

    def shift_shape(self, x, y):
        self.x += x
        self.y += y
        for i in range(len(self.shape)):
            self.shape[i] = (self.shape[i][0] + x, self.shape[i][1] + y)

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
        self.set_size(self.current_size)

    def point_to(self, x, y):
        self.point_in_direction(x - self.x, y - self.y)

    def move_forward(self, dt):
        x, y = math.cos(self.angle) * self.movement_speed * dt, math.sin(self.angle) * self.movement_speed * dt
        self.shift_shape(x, y)

    def receive_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def update(self, dt, touching_mouse=False):
        if self.health <= 0:
            return 0
        if touching_mouse:
            self.current_colour = (250, 100, 100)
        else:
            self.current_colour = self.colour
        # self.angle += math.pi/16 * dt
        # self.set_size(self.current_size)
        # self.angle %= 2 * math.pi
        return 1  # 1 = Ok, 0 = Entity needs to be removed


class Bullet:

    def __init__(self, pointer, source=None, bullet_type=None):
        # Attributes
        self.source = source  # Entity that fired the bullet
        self.entity_type = "bullet"
        self.pointer = pointer

        # Position
        if self.source is None:
            self.x, self.y, self.angle = 0, 0, 0  # Angle is in radians
        else:
            (self.x, self.y), self.angle = self.source.get_position(), self.source.angle

        # Default Display
        if bullet_type is None:
            self.mapping = ((1, math.pi / 6), (1, 5 * math.pi / 6), (1, - 5 * math.pi / 6), (1, -math.pi / 6))  # (radius, angle in radians)
            self.size = 16  # Scale factor for mapping
            self.colour = (0, 0, 0)
        else:
            self.mapping = projectile_data[bullet_type][1]
            self.size = projectile_data[bullet_type][2]
            self.colour = projectile_data[bullet_type][0]
        self.name = "Bullet"
        self.sprite_type = "bullet"

        # Animations
        self.shape = []  # List of xy coordinates for each vertex of the entity
        self.current_size = self.size
        self.set_size(self.size)
        self.current_colour = self.colour

        # Stats
        if bullet_type is None:
            self.movement_speed = 540
            self.range = 2000
        else:
            self.movement_speed = projectile_data[bullet_type][3]
            self.range = projectile_data[bullet_type][4]
        self.units_travelled = 0

    def scale_entity(self, entity_scale):
        self.size *= entity_scale
        self.current_size = self.size
        self.movement_speed *= entity_scale

    def get_draw_data(self):
        return self.sprite_type, (self.x, self.y, self.angle), self.shape, self.current_colour

    def get_position(self):
        return self.x, self.y

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.set_size(self.current_size)

    def set_size(self, size):
        self.shape = []
        self.current_size = size
        for i in self.mapping:
            radius, angle = i
            point = ((size * radius * math.cos(angle + self.angle) + self.x),
                     (size * radius * math.sin(angle + self.angle) + self.y))
            self.shape.append(point)

    def point_in_direction(self, x_dif, y_dif):
        if y_dif < 0:
            self.angle = - math.pi / 2 - math.atan(x_dif / y_dif)
        else:
            if y_dif != 0:
                self.angle = math.pi / 2 - math.atan(x_dif / y_dif)
        self.set_size(self.current_size)

    def point_to(self, x, y):
        self.point_in_direction(x - self.x, y - self.y)

    def move_forward(self, dt):
        self.x += math.cos(self.angle) * self.movement_speed * dt
        self.y += math.sin(self.angle) * self.movement_speed * dt
        self.units_travelled += self.movement_speed * dt
        self.set_size(self.size)

    def update(self, dt, touching_mouse=False):
        if self.units_travelled < self.range:
            self.move_forward(dt)
        else:
            return 0
        return 1
