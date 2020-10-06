import math

root_two = 2**(1/2)
one_over_r2 = 1 / root_two

class Entity:

    def __init__(self):
        self.x, self.y, self.angle = 0, 0, 0

        self.acceleration = 500
        self.deceleration = 1000

        self.velocity = 0
        self.max_speed = 600

        self.fall_velocity = 0

        self.w_pressed = False
        self.a_pressed = False
        self.d_pressed = False

        self.touching_ceiling = False
        self.touching_ground = False
        self.gravity = 1700
        self.jump_strength = 900
        self.terminal_velocity = 1500

        self.touching_left_wall = False
        self.touching_right_wall = False

        self.width = 100
        self.length = 100
        self.size = self.width * 1 / math.sqrt(2)

    def scale_entity(self, scale):
        # self.acceleration *= scale
        # self.deceleration *= scale
        # self.max_speed *= scale
        # self.gravity *= scale
        # self.jump_strength *= scale
        # self.terminal_velocity *= scale
        self.width *= scale
        self.length *= scale
        self.size = self.width * 1 / math.sqrt(2)

    def get_position(self):
        return self.x, self.y

    def get_rect(self):
        return self.x - self.width / 2, self.y - self. length / 2, self.width, self.length

    def get_polygon(self):
        polygon = []
        for i in range(4):
            angle = math.pi / 4 + i * math.pi/2 + self.angle
            point = (self.x + math.cos(angle) * self.size, self.y + math.sin(angle) * self.size)
            polygon.append(point)
        return polygon

    def jump(self):
        self.player.fall_velocity = -500

    def update(self, dt):
        if self.a_pressed and not self.d_pressed:
            self.velocity -= self.acceleration * dt
            if self.velocity < -1 * self.max_speed:
                self.velocity = -1 * self.max_speed
            elif self.velocity > 0:
                self.velocity -= self.deceleration * dt

        elif self.d_pressed and not self.a_pressed:
            self.velocity += self.acceleration * dt
            if self.velocity > self.max_speed:
                self.velocity = self.max_speed
            elif self.velocity < 0:
                self.velocity += self.deceleration * dt

        else:
            shift = self.deceleration * dt
            if self.velocity - shift > 0:
                self.velocity -= shift

            elif self.velocity + shift < 0:
                self.velocity += shift

            else:
                self.velocity = 0

        if self.w_pressed:
            if self.touching_ground and self.fall_velocity == 0:
                self.fall_velocity += self.jump_strength
                self.touching_ground = False

        if self.touching_ground:
            self.fall_velocity = 0
        else:
            self.fall_velocity -= self.gravity * dt
            if self.fall_velocity < -1 * self.terminal_velocity:
                self.fall_velocity = -1 * self.terminal_velocity

        if self.touching_ceiling and self.fall_velocity > 0:
            self.fall_velocity = 0

        if self.touching_left_wall:
            if self.velocity < 0:
                self.velocity = 0

        if self.touching_right_wall:
            if self.velocity > 0:
                self.velocity = 0

        self.x += math.cos(self.angle) * self.velocity * dt
        self.y += math.sin(self.angle) * self.velocity * dt

        self.y += math.sin(self.angle + math.pi / 2) * self.fall_velocity * dt

        self.w_pressed = False
        self.a_pressed = False
        self.d_pressed = False

        self.touching_ground = False
        self.touching_ceiling = False
        self.touching_left_wall = False
        self.touching_right_wall = False
