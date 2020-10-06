import math, json, pygame
from src import filePath, gameEngine
from src.entities import baseEntity


class Scene:

    def __init__(self, resolution, fps, debug, player_data=None):
        self.resolution = resolution
        self.targetFps = fps
        self.debug = debug

        self.fpsScale = 16 * fps / 1000

        self.engine = gameEngine.Engine(resolution, fps, debug)

        entity_scale = self.resolution[0] / 3200

        positions = [
            [1, 1],
            [3, 1],
            [5, 1],
            [7, 1],
            [9, 1],
            [11, 1],
            [13, 1],
            [1, 12],
            [3, 12],
            [5, 12],
        ]

        for i in range(len(positions)):
            positions[i] = [positions[i][0] * 192, positions[i][1] * 192]

        player = self.engine.add_entity("player")
        player.set_position(192, 192)
        player.scale_position(entity_scale)
        for i in range(10):
            entity = self.engine.add_entity("enemies")
            entity.set_position(positions[i][0], positions[i][1])
            entity.scale_position(entity_scale)

        if player_data is not None:
            self.engine.set_player_data(player_data)

        pygame.mouse.set_visible(True)

    def update(self, surface, events, dt, time_elapsed):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    surface.fill((0, 0, 0))
                    return "switch", "main menu", None

        self.engine.update(surface, events, dt, time_elapsed)

        return 0  # No information to pass back
