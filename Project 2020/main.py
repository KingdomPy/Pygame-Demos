import pygame
import cProfile

fps = 60
debug = True
resolution = (1600, 900)

def start_game():
    pygame.init()
    surface = pygame.display.set_mode(resolution)

    from src.scenes import mainMenu, test, tutorial

    scenes = {"main menu": mainMenu, "test": tutorial}
    pseudo_data = [0, 18220, 99999, 0, [0, 1], [[0, 1], [1, 1], [2, 1], [3, 1], [4, 1]], 20,
                   {'equipped techniques': ['Repair', 'Test', 'Test', 'Test'], 'equipped talents': ['Spray'],
                    'technique deck': ['Surge']}
                   ]
    current_scene = scenes["test"].Scene(resolution, fps, debug, pseudo_data)
    # current_scene = scenes["main menu"].Scene(resolution, fps, debug)

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
            if time_elapsed > 16:
                print(time_elapsed)
            dt_counter += dt
            time_elapsed_counter += time_elapsed
            if dt_counter > 1000:
                current_fps = round(fps * dt_counter/time_elapsed_counter)
                dt_counter = 0
                time_elapsed_counter = 0
            pygame.time.delay(wait)

        else:
            instruction, argument, player_data = scene_status
            if instruction == "switch":
                pygame.display.flip()
                current_scene = scenes[argument].Scene(current_scene.resolution, fps, debug,
                                                       player_data)  # Load the new scene


if __name__ == "__main__":
    start_game()

