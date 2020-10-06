import math

root_two = 2**(1/2)
one_over_r2 =1 / root_two


class Tile:

    def __init__(self, width, length, sprite_code):
        self.x, self.y, self.angle = 0, 0, 0

        self.width = width
        self.length = length

        self.sprite_code = sprite_code

        self.collidable = True
        self.visible = True

    def get_position(self):
        return self.x, self.y

    def get_rect(self):
        return self.x - self.width / 2, self.y - self. length / 2, self.width, self.length

    def jump(self):
        self.player.fall_velocity = -500

    def update(self, dt):
        # Animations
        pass
