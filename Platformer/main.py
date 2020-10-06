import pygame

fps = 60
debug = False
resolution = (1280, 720) # 1920, 1080 | 960, 540

if __name__ == "__main__":
    pygame.init()
    surface = pygame.display.set_mode(resolution)

    from scripts.scenes import GameEngine, MapCreator, TestEngine

    scenes = {"game": GameEngine, "map creator": MapCreator, "test": TestEngine}

    current_scene = scenes["test"].Scene(resolution, fps, debug)

    dt = 16
    current_fps = 60
    dt_counter = 0
    time_elapsed_counter = 0

    while True:
        startTime = pygame.time.get_ticks()

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
    
        scene_status = current_scene.update(surface, events, dt, current_fps)
        if scene_status == 0:
            pygame.display.flip()

            time_elapsed = pygame.time.get_ticks() - startTime

            wait = max(16 - time_elapsed, 0)
            dt = max(16, time_elapsed)

            dt_counter += dt
            time_elapsed_counter += time_elapsed
            if dt_counter > 1000:
                current_fps = round(fps * dt_counter / time_elapsed_counter)
                dt_counter = 0
                time_elapsed_counter = 0
                if current_fps < 60:
                    print(current_fps)
            pygame.time.delay(wait)

        else:
            instruction, argument, player_data = scene_status
            if instruction == "switch":
                pygame.display.flip()
                current_scene = scenes[argument].Scene(current_scene.resolution, fps, debug,
                                                       player_data)  # Load the new scene

