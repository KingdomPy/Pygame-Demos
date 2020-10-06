import math, json, pygame
from src import filePath


class Scene:

    def __init__(self, resolution, fps, debug, player_data=None):
        self.resolution = resolution
        self.targetFps = fps
        self.debug = debug

        self.fpsScale = 16 * fps / 1000

        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.mouse.set_visible(False)

        asset_path = filePath.setPath(filePath.getRootFolder(2), ["lib"])

        self.fonts = [
            filePath.setPath(asset_path, ["fonts", "Coda-Regular.ttf"]),
        ]

        self.menuSounds = [
            pygame.mixer.Sound(filePath.setPath(asset_path, ["sounds", "system sound effects", "error.wav"])),
            pygame.mixer.Sound(filePath.setPath(asset_path, ["sounds", "system sound effects", "menu back.wav"])),
            pygame.mixer.Sound(filePath.setPath(asset_path, ["sounds", "system sound effects", "menu open.wav"])),
            pygame.mixer.Sound(filePath.setPath(asset_path, ["sounds", "system sound effects", "menu scroll.wav"])),
            pygame.mixer.Sound(filePath.setPath(asset_path, ["sounds", "system sound effects", "select.wav"])),
        ]

        menuMusic = pygame.mixer.music.load(filePath.setPath(asset_path, ["sounds", "music", "kh3-Dearly Beloved.mp3"]))

        self.musicStarted = False

        self.controls = {"up": [pygame.K_w], "left": [pygame.K_a], "right": [pygame.K_d], "down": [pygame.K_s],
                         "SQUARE": [pygame.K_j], "CIRCLE": [pygame.K_l, 1], "CROSS": [pygame.K_k, 0],
                         "TRIANGLE": [pygame.K_i, 3],
                         "start": [pygame.K_p, 7], "home": [pygame.K_ESCAPE, 6],
                         "L1": [pygame.K_q, 4], "R1": [pygame.K_e, 5]}

        self.playSounds = 1
        self.playMusic = 1
        self.customCursor = 1

        self.supported_resolutions = ("900x450", "1280x720", "1600x900")
        current_resolution = str(self.resolution[0]) + "x" + str(self.resolution[1])
        self.selected_resolution = self.supported_resolutions.index(current_resolution)

        # Assets
        self.assets = [pygame.image.load(
                           filePath.setPath(asset_path, ["title screen", "logo.png"])).convert_alpha(),
                       pygame.image.load(
                           filePath.setPath(asset_path, ["title screen", "overlay.png"])).convert_alpha(),
                       pygame.image.load(filePath.setPath(asset_path, ["background", "cursor.png"])).convert_alpha(),
                       pygame.image.load(
                           filePath.setPath(asset_path, ["player", "emblems", "vanguard.png"])).convert_alpha(),
                       pygame.image.load(
                           filePath.setPath(asset_path, ["player", "emblems", "engineer.png"])).convert_alpha(),
                       pygame.image.load(
                           filePath.setPath(asset_path, ["player", "emblems", "stealth.png"])).convert_alpha(),
                       ]

        self.cursor = pygame.image.load(filePath.setPath(asset_path, ["background", "cursor.png"])).convert_alpha()
        self.cursor = pygame.transform.smoothscale(self.cursor, (40, 40))

        self.cursorTouching = [None]

        self.instance = "main screen"  # Controls which UI is loaded

        self.savedData = self.load_saves()

        self.resize_assets()

        self.stage = "startUp1"
        self.clock = 0
        self.closing = False
        self.open = True

    def resize_assets(self):
        asset_scale = self.resolution[0] / 1600

        #Fonts
        self.fontMain = pygame.font.Font(self.fonts[0], round(4 + 20 * asset_scale))
        self.fontSub = pygame.font.Font(self.fonts[0], round(4 + 16 * asset_scale))

        self.emblems = []
        # Emblems
        for i in range(3, 6):  # Scale images
            self.emblems.append(pygame.transform.smoothscale(self.assets[i], self.resolution))

        # Start up animation
        self.startupImage = pygame.transform.smoothscale(self.assets[0], self.resolution)
        self.startupRect = self.startupImage.get_rect()
        self.startupRect.center = (round(self.resolution[0] / 2), round(self.resolution[1] / 2))

        # Title screen
        self.background = pygame.transform.smoothscale(self.assets[1], self.resolution)

        # Calculations needed for graph coordinates
        boxSpace = self.resolution[1] / 3 - 110
        boxShift = (boxSpace - 3 * 35) / 2 + self.resolution[1] / 3 + 70
        boxShift2 = (boxSpace - 2 * 35) / 2 + self.resolution[1] / 3 + 70
        # i*45+boxShift  #Box Widths = 168, 242, 119

        self.graph = {
            "NEW GAME": {"up": "CONFIG", "down": "LOAD",
                         "value": (self.resolution[0] - 200, self.resolution[1] - 4.6 * self.resolution[1] / 20 + 5),
                         "next": "Normal",
                         "previous": ""},  # Controls where the controller should take the cursor
            "LOAD": {"up": "NEW GAME", "down": "CONFIG",
                     "value": (self.resolution[0] - 200, self.resolution[1] - 3.2 * self.resolution[1] / 20 + 5),
                     "next": "save1",
                     "previous": ""},
            "CONFIG": {"up": "LOAD", "down": "NEW GAME",
                       "value": (self.resolution[0] - 200, self.resolution[1] - 1.8 * self.resolution[1] / 20 + 5),
                       "next": "Sound",
                       "previous": ""},

            "Normal": {"up": "Extreme", "down": "Hard", "value": (self.resolution[0] * 0.25 + 75, boxShift),
                       "next": "save1",
                       "previous": "NEW GAME"},
            "Hard": {"up": "Normal", "down": "Extreme", "value": (self.resolution[0] * 0.25 + 75, 45 + boxShift),
                     "next": "save1", "previous": "NEW GAME"},
            "Extreme": {"up": "Hard", "down": "Normal", "value": (self.resolution[0] * 0.25 + 75, 90 + boxShift),
                        "next": "save1", "previous": "NEW GAME"},

            "save1": {"up": "save6", "down": "save2", "value": (self.resolution[0] * 0.12, self.resolution[1] * 0.25),
                      "next": "Yes", "previous": ""},
            "save2": {"up": "save1", "down": "save3", "value": (self.resolution[0] * 0.12, self.resolution[1] * 0.35),
                      "next": "Yes", "previous": ""},
            "save3": {"up": "save2", "down": "save4", "value": (self.resolution[0] * 0.12, self.resolution[1] * 0.45),
                      "next": "Yes", "previous": ""},
            "save4": {"up": "save3", "down": "save5", "value": (self.resolution[0] * 0.12, self.resolution[1] * 0.55),
                      "next": "Yes", "previous": ""},
            "save5": {"up": "save4", "down": "save6", "value": (self.resolution[0] * 0.12, self.resolution[1] * 0.65),
                      "next": "Yes", "previous": ""},
            "save6": {"up": "save5", "down": "save1", "value": (self.resolution[0] * 0.12, self.resolution[1] * 0.75),
                      "next": "Yes", "previous": ""},

            "Sound": {"up": "Custom Cursor", "down": "Music", "value": (self.resolution[0] * 0.25 + 112, boxShift),
                      "next": "Sound", "previous": "CONFIG"},
            "Music": {"up": "Sound", "down": "Custom Cursor", "value": (self.resolution[0] * 0.25 + 112, 45 + boxShift),
                      "next": "Music", "previous": "CONFIG"},
            "Custom Cursor": {"up": "Music", "down": "Sound", "value": (self.resolution[0] * 0.25 + 112, 90 + boxShift),
                              "next": "Custom Cursor", "previous": "CONFIG"},

            "Yes": {"up": "No", "down": "No", "value": (self.resolution[0] * 0.25 + 56.5, boxShift2), "next": "",
                    "previous": ""},
            "No": {"up": "Yes", "down": "Yes", "value": (self.resolution[0] * 0.25 + 56.5, 45 + boxShift2), "next": "",
                   "previous": ""},
        }
        self.currentNode = "NEW GAME"

        # Gradients
        self.gradient = pygame.Surface(self.resolution, pygame.SRCALPHA)
        optionsRect = (self.resolution[0] * 0.4, self.resolution[1] / 20)  # Constant for ui sizes
        self.rectangleSurface = pygame.Surface(optionsRect, pygame.SRCALPHA)
        self.squareSurface = pygame.Surface((optionsRect[1], optionsRect[1]), pygame.SRCALPHA)
        self.highlightSurface = pygame.Surface((optionsRect[1] * 0.6, optionsRect[1] * 0.6), pygame.SRCALPHA)
        self.lineSurface = pygame.Surface((self.resolution[0] - 30, 3), pygame.SRCALPHA)
        self.uiBox = pygame.Surface((self.resolution[0], self.resolution[1] / 3), pygame.SRCALPHA)
        self.uiBox.fill((0, 0, 0, 170))
        self.saveImage = pygame.Surface((self.resolution[0] * 0.8, self.resolution[1] * 0.1), pygame.SRCALPHA)
        self.saveImageLine = pygame.Surface((self.resolution[0] * 0.8, 3), pygame.SRCALPHA)

        # draw main option pre-calculations
        self.yCalculations = [self.resolution[1] - 1.8 * optionsRect[1], self.resolution[1] - 3.2 * optionsRect[1],
                              self.resolution[1] - 4.6 * optionsRect[1]]
        self.mainOptionCalculations = [
            ((self.resolution[0] + 1 - optionsRect[0], self.yCalculations[0]), (30, self.yCalculations[0]),
             (30 + optionsRect[1] * 0.2, self.yCalculations[0] + optionsRect[1] * 0.2),
             (30, self.yCalculations[0] + optionsRect[1] - 3)),
            ((self.resolution[0] + 1 - optionsRect[0], self.yCalculations[1]), (30, self.yCalculations[1]),
             (30 + optionsRect[1] * 0.2, self.yCalculations[1] + optionsRect[1] * 0.2),
             (30, self.yCalculations[1] + optionsRect[1] - 3)),
            ((self.resolution[0] + 1 - optionsRect[0], self.yCalculations[2]), (30, self.yCalculations[2]),
             (30 + optionsRect[1] * 0.2, self.yCalculations[2] + optionsRect[1] * 0.2),
             (30, self.yCalculations[2] + optionsRect[1] - 3))
        ]

        # draw ui box pre-calculations
        self.uiBoxCalculations = [
            (0, self.resolution[1] / 3),
            ((0, self.resolution[1] / 3 - 5 * asset_scale), (self.resolution[0], self.resolution[1] / 3 - 5 * asset_scale)),
            ((0, 2 * self.resolution[1] / 3), (self.resolution[0], 2 * self.resolution[1] / 3)),
            (self.resolution[0] / 2, 2 * self.resolution[1] / 3 - 25 * asset_scale),
            (self.resolution[0] / 2, self.resolution[1] / 3 + 30 * asset_scale),
            self.resolution[1] / 3 - 110 * asset_scale,
            self.resolution[1] / 3 + 70 * asset_scale,
            45 * asset_scale,
            35 * asset_scale,
            round(3 * asset_scale),
        ]

        # load menu pre-calculations
        self.load_menuCalculations = [
            pygame.Rect(self.resolution[0] * 0.1, self.resolution[1] * 0.2, self.resolution[0] * 0.8,
                        self.resolution[1] * 0.6),
            self.resolution[1] * 0.1,
            pygame.Rect(self.resolution[0] * 0.1, self.resolution[1] * 0.2, self.resolution[0] * 0.8,
                        self.resolution[1] * 0.1),
            pygame.Rect(self.resolution[0] * 0.1, self.resolution[1] * 0.2 + self.resolution[1] * 0.1,
                        self.resolution[0] * 0.8,
                        self.resolution[1] * 0.1),
            pygame.Rect(self.resolution[0] * 0.1, self.resolution[1] * 0.2 + self.resolution[1] * 0.2,
                        self.resolution[0] * 0.8,
                        self.resolution[1] * 0.1),
            pygame.Rect(self.resolution[0] * 0.1, self.resolution[1] * 0.2 + self.resolution[1] * 0.3,
                        self.resolution[0] * 0.8,
                        self.resolution[1] * 0.1),
            pygame.Rect(self.resolution[0] * 0.1, self.resolution[1] * 0.2 + self.resolution[1] * 0.4,
                        self.resolution[0] * 0.8,
                        self.resolution[1] * 0.1),
            pygame.Rect(self.resolution[0] * 0.1, self.resolution[1] * 0.2 + self.resolution[1] * 0.5,
                        self.resolution[0] * 0.8,
                        self.resolution[1] * 0.1),
        ]

        self.load_menuYCalculations = [
            self.resolution[1] * 0.2,
            self.resolution[1] * 0.2 + self.resolution[1] * 0.1,
            self.resolution[1] * 0.2 + self.resolution[1] * 0.2,
            self.resolution[1] * 0.2 + self.resolution[1] * 0.3,
            self.resolution[1] * 0.2 + self.resolution[1] * 0.4,
            self.resolution[1] * 0.2 + self.resolution[1] * 0.5,
        ]

    def update(self, surface, events, dt, time_elapsed):
        if not self.musicStarted:
            pygame.mixer.music.play(-1)
            self.musicStarted = True

        if self.stage == "startUp1":
            if self.clock < 280 * 16 * self.fpsScale:  # Emulate for loop
                i = self.clock // (16 * self.fpsScale)
                if i < 75:  # Up till 1.5 seconds
                    self.startupImage.set_alpha(i * 4 + 1)
                    surface.blit(self.startupImage, self.startupRect)

            else:
                self.stage = "startUp2"
                self.clock = 0  # Reset the clock

        elif self.stage == "startUp2":
            if self.clock < 60 * 16 * self.fpsScale:  # Emulate for loop
                i = self.clock // (16 * self.fpsScale)
                self.gradient.fill((0, 0, 0, i * 4 + 1))
                surface.blit(self.gradient, (0, 0))

            else:
                self.stage = "titleScreen transition"
                self.clock = 0  # Reset the clock

        elif self.stage == "titleScreen transition":
            if self.clock < 63 * 16 * self.fpsScale:  # Emulate for loop
                i = self.clock // (16 * self.fpsScale)
                self.draw_main_option(surface, 4.6, (0, 0), "NEW GAME")
                self.draw_main_option(surface, 3.2, (0, 0), "LOAD")
                self.draw_main_option(surface, 1.8, (0, 0), "CONFIG")

                surface.blit(self.background, (0, 0))

                self.gradient.fill((255, 255, 255, 249 - i * 3))
                surface.blit(self.gradient, (0, 0))
            else:
                if self.customCursor == 1:
                    pygame.mouse.set_visible(False)
                else:
                    pygame.mouse.set_visible(True)

                # Test the gamepad
                self.gamePads = []
                for i in range(0, pygame.joystick.get_count()):
                    self.gamePads.append(pygame.joystick.Joystick(i))
                    self.gamePads[-1].init()
                    if self.debug:
                        print("Detected gamepad '", self.gamePads[-1].get_name(), "'")

                self.stage = "titleScreen"
                clock = 0  # Reset the clock

        elif self.stage == "titleScreen":
            for event in events:
                # Test the gamepad
                if event.type == pygame.JOYBUTTONDOWN:
                    if self.debug:
                        print("button:", event.button)
                    if event.button == 0:  # Advance button
                        destination = self.graph[self.currentNode]["next"]
                        if destination != "":
                            previousNode = self.currentNode
                            if previousNode != destination:  # Prevents loops
                                self.currentNode = destination
                                self.graph[self.currentNode]["previous"] = previousNode
                                startNode = self.graph[self.currentNode]["down"]
                                while startNode != self.currentNode:  # Set all the options previous settings
                                    self.graph[startNode]["previous"] = previousNode
                                    startNode = self.graph[startNode]["down"]
                                if previousNode == "LOAD":
                                    for i in range(6):
                                        self.graph["save" + str(i + 1)]["next"] = ""
                                elif self.graph[previousNode]["previous"] == "NEW GAME":
                                    for i in range(6):
                                        self.graph["save" + str(i + 1)]["next"] = "Yes"
                        elif self.currentNode == "No":
                            self.currentNode = self.graph[self.currentNode]["previous"]
                        self.handle_input()
                        if self.debug:
                            print("option:", self.currentNode)

                    if event.button == 1:
                        if self.graph[self.currentNode]["previous"] != "":
                            x, y = 0, 0
                            self.currentNode = self.graph[self.currentNode]["previous"]
                            if self.currentNode == "NEW GAME" or self.currentNode == "LOAD" or self.currentNode == "CONFIG":
                                self.cursorTouching[0] = "0"
                            elif self.graph[self.currentNode]["next"][:2] == "sa":
                                self.cursorTouching[0] = "1"
                            elif self.currentNode[:2] == "sa":
                                self.cursorTouching = ["CREATEFILE", "No"]
                            else:
                                self.cursorTouching[0] = "0"
                            self.handle_input()
                        else:
                            pygame.mixer.Sound.play(self.menuSounds[1])  # back

                        if self.debug:
                            print("option:", self.currentNode)

                if event.type == pygame.JOYHATMOTION:
                    dpad = self.gamePads[0].get_hat(0)
                    if self.debug:
                        print("dpad:", dpad)
                    if dpad[1] == 1:
                        self.currentNode = self.graph[self.currentNode]["up"]
                    elif dpad[1] == -1:
                        self.currentNode = self.graph[self.currentNode]["down"]

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if len(self.gamePads) == 0:
                        self.handle_input()

            if self.instance == "startGame":
                if not self.closing:
                    pygame.mixer.music.fadeout(3000)
                    self.closing = True
                if self.clock < 30 * 16 * self.fpsScale:  # Emulate for loop
                    i = self.clock // (16 * self.fpsScale)
                    self.gradient.fill((0, 0, 0, i * 8 + 1))
                    surface.blit(self.gradient, (0, 0))
                    self.drawnLoadingText = False
                else:
                    if not self.drawnLoadingText:
                        text = self.fontMain.render("LOADING", True, (240, 240, 240))
                        textRect = text.get_rect()
                        textRect.bottomright = (self.resolution[0] * 0.95, self.resolution[1] - 8)
                        surface.blit(text, textRect)
                        self.drawnLoadingText = True
                        return "switch", "test", self.playerData  # Exit the scene

            if not self.closing:
                surface.fill((255, 255, 255))  # Make screen blank (white)
                surface.blit(self.background, (0, 0))  # Title

                if len(self.gamePads) > 0:
                    x, y = self.graph[self.currentNode]["value"]
                    y += 4  # move y down slightlty
                else:
                    x, y = pygame.mouse.get_pos()  # Get mouse coordinates

                if self.instance == "main screen":
                    self.draw_main_option(surface, 4.6, (x, y), "NEW GAME")
                    self.draw_main_option(surface, 3.2, (x, y), "LOAD")
                    self.draw_main_option(surface, 1.8, (x, y), "CONFIG")

                else:  # Render the gui but prevent selection and collision
                    self.draw_main_option(surface, 4.6, (0, 0), "NEW GAME")
                    self.draw_main_option(surface, 3.2, (0, 0), "LOAD")
                    self.draw_main_option(surface, 1.8, (0, 0), "CONFIG")

                # Instances
                if self.instance == "newGame":
                    self.draw_ui_box(surface, (x, y), "Select a game difficulty level.", "(The difficulty can not be changed.)",
                                     [
                                         ("Normal", "Standard difficulty, recommended for new players."),
                                         ("Hard", "Enemy stats are increased to x1.3."),
                                         ("Extreme",
                                          "Enemy stats are increased to x1.5, damage increased to x1.25, EXP gain decreased to x0.8.")
                                     ])

                elif self.instance == "createFile":
                    self.draw_load_menu(surface, (x, y), 1)

                elif self.instance == "load":
                    self.draw_load_menu(surface, (x, y))

                elif self.instance == "confirm":
                    self.draw_ui_box(surface, (x, y), "CREATE A NEW SAVE", self.createTextOption,
                                     [
                                         ("Yes", "Begin your new save with " + self.fileType.upper() + " difficulty."),
                                         ("No", "Return to save menu."),
                                     ])

                elif self.instance == "config":
                    self.draw_ui_box(surface, (x, y), "Configure your options.", "(These can be changed in-game.)",
                                     [
                                         ("Sound", "Toggle if sound effects are played."),
                                         ("Music", "Toggle if music is played."),
                                         ("Custom Cursor", "Toggle between custom cursor and your device's cursor."),
                                         (self.supported_resolutions[self.selected_resolution], "Cycle through the resolutions, exit to save")
                                     ],
                                     [
                                         ("TOGGLE", self.playSounds, "playSounds"),
                                         ("TOGGLE", self.playMusic, "playMusic"),
                                         ("TOGGLE", self.customCursor, "customCursor"),
                                         ("OPTIONS", self.selected_resolution, "selectResolution")
                                     ])

                if self.customCursor:  # Render custom mouse if the option is on
                    cursorRect = self.cursor.get_rect()
                    cursorRect.center = (x, y)
                    surface.blit(self.cursor, cursorRect)

        self.clock += dt
        return 0 # No information to pass back

    def load_saves(self):
        saves = []
        path = filePath.getRootFolder(2)
        for i in range(6):  # 6 = maximum number of saves
            try:  # Load save files
                # File formate = [difficulty, level, money, shipType, emblems, items, current chapter]
                saveFile = open(filePath.setPath(path, ["data", "saves", "save" + str((i + 1)) + ".txt"]),
                                "r").readlines()
                try:  # Check if the save is interperatble
                    save = 0
                    savedData = json.loads(saveFile[0])
                    if 0 <= savedData[0] <= 2:  # difficulty
                        if 0 <= savedData[1] <= 260770:  # exp
                            if 0 <= savedData[2] <= 99999:  # money
                                if -1 <= savedData[3] <= 2:  # shipType
                                    if -1 <= savedData[4][0] <= 2 and -1 <= savedData[4][1] <= 2:  # emblems
                                        if 0 <= savedData[6] <= 21:  # current chapter
                                            saves.append(savedData)
                                            save = 1
                    if save == 0:
                        saves.append("corrupted")

                except:  # Returned save corrupted
                    saves.append("corrupted")

            except:  # Skip if save not found
                saves.append(0)
        if self.debug:
            for i in range(len(saves)): print(saves[i])
            print("")
        return saves

    def draw_main_option(self, surface, y, mouse_coordinates, text="TEST"):
        optionsRect = (self.resolution[0] * 0.4, self.resolution[1] / 20)  # Constant for ui sizes

        if y == 1.8:
            y = self.yCalculations[0]
            index = 0
        elif y == 3.2:
            y = self.yCalculations[1]
            index = 1
        elif y == 4.6:
            y = self.yCalculations[2]
            index = 2

        if mouse_coordinates[0] >= 30 and y < mouse_coordinates[1] < (y + optionsRect[1]):  # Calculate if touching the mouse pointer
            colours = ((113, 169, 247, 140), (0, 0, 0, 255), (
                113, 169, 247, 255))  # Rectangle, Square & Line, Hightlight #230,250,252 | 113,169,247 Colour Codes
            textColour = (0, 0, 0)
            if self.cursorTouching[0] != text:
                if self.playSounds:
                    pygame.mixer.Sound.play(self.menuSounds[3])  # menu scroll
            self.cursorTouching = [text]
        else:
            colours = ((160, 160, 160, 190), (160, 160, 160, 190), (0, 0, 0, 0))  # Rectangle, Square & Line, Highlight
            textColour = (175, 175, 175)
            if self.cursorTouching[0] == text:  # clear touching if no longer touching
                self.cursorTouching = [None]

        self.rectangleSurface.fill(colours[0])
        self.squareSurface.fill(colours[1])
        self.highlightSurface.fill(colours[2])
        self.lineSurface.fill(colours[1])

        surface.blit(self.rectangleSurface, self.mainOptionCalculations[index][0])
        surface.blit(self.squareSurface, (30, y))
        surface.blit(self.highlightSurface, self.mainOptionCalculations[index][2])
        surface.blit(self.lineSurface, self.mainOptionCalculations[index][3])

        text = self.fontMain.render(text, True, textColour)
        text_rect = text.get_rect()
        text_rect.topleft = (30 + optionsRect[1] + 10, y)
        surface.blit(text, text_rect)

    def draw_ui_box(self, surface, mouse_coordinates, title="Title", text="text", options=[("Test1", "Hover on me.")], buttonScripts=[]):
        iterations = len(options) - len(buttonScripts)  # Load button scripts
        for i in range(iterations):
            buttonScripts.append("")

        # Draw the ui box
        self.gradient.fill((0, 0, 0, 200))
        surface.blit(self.gradient, (0, 0))
        surface.blit(self.uiBox, self.uiBoxCalculations[0])
        pygame.draw.line(surface, (168, 149, 229), self.uiBoxCalculations[1][0], self.uiBoxCalculations[1][1],
                         7)  # Top border
        pygame.draw.line(surface, (168, 149, 229), self.uiBoxCalculations[2][0], self.uiBoxCalculations[2][1],
                         7)  # Bottom border

        # Check if touching outside the menu
        if mouse_coordinates[1] < self.resolution[1] / 3 - 7 or mouse_coordinates[1] > 2 * self.resolution[1] / 3 + 7:
            self.cursorTouching = ["0"]  # close the ui

        text = self.fontMain.render(text, True, (236, 239, 26))  # Information text
        title = self.fontMain.render(title, True, (240, 240, 240))  # Tile text

        textRect = text.get_rect()  # Information text box
        textRect.center = self.uiBoxCalculations[3]
        surface.blit(text, textRect)  # Information text render
        titleRect = title.get_rect()
        titleRect.center = self.uiBoxCalculations[4]
        surface.blit(title, titleRect)  # Information text render

        longestText = 0
        renderedText = []
        for i in range(len(options)):  # Find the option with the longest text length
            renderedText.append(self.fontMain.render(options[i][0], True, (240, 240, 240)))
            length = renderedText[i].get_rect()[2]  # 2 = width of the text
            if length > longestText:
                longestText = length
        # Set width of the button using the longest length so that all buttons are the same width
        width = longestText + 80  # 40 on each side
        boxSpace = self.uiBoxCalculations[5]  # The vertical length of space the buttons will be placed in
        numOfOptions = len(options)
        boxShift = (boxSpace - numOfOptions * self.uiBoxCalculations[8]) / 2 + self.uiBoxCalculations[6]
        # Creates equal gap between title and the text
        for i in range(numOfOptions):
            colours = ((10, 5, 25), (120, 120, 120))  # Box, Text colours

            optionBox = pygame.Rect(0, 0, width, self.uiBoxCalculations[8])  # x, y, width, length
            optionBox.center = (self.uiBoxCalculations[6], i * self.uiBoxCalculations[7] + boxShift)

            if optionBox.collidepoint(mouse_coordinates):  # change colours if colliding with mouse

                if buttonScripts[i] == "":  # Check if it is an ordinary button
                    colours = ((56, 9, 5), (240, 240, 240))  # Box, Text colours
                    pygame.draw.rect(surface, (168, 24, 11), (
                        optionBox[0] - self.uiBoxCalculations[9], optionBox[1] - self.uiBoxCalculations[9],
                        optionBox[2] + self.uiBoxCalculations[9] * 2, optionBox[3] + self.uiBoxCalculations[9] * 2))
                        # Highlighted border
                    if self.cursorTouching != ["CREATEFILE", options[i][0]]:
                        if self.playSounds:
                            pygame.mixer.Sound.play(self.menuSounds[3])  # menu scroll
                    self.cursorTouching = ["CREATEFILE", options[i][0]]

                else:  # Run the button's script
                    script = buttonScripts[i]
                    if script[0] == "TOGGLE":
                        if script[1] == 1:
                            colours = ((72, 10, 5), (236, 239, 26))  # Box, Text colours
                            pygame.draw.rect(surface, (234, 79, 18), (
                                optionBox[0] - self.uiBoxCalculations[9], optionBox[1] - self.uiBoxCalculations[9],
                                optionBox[2] + self.uiBoxCalculations[9] * 2,
                                optionBox[3] + self.uiBoxCalculations[9] * 2))
                        else:
                            if self.cursorTouching != ["TOGGLE", script[2]]:
                                colours = ((10, 5, 25), (120, 120, 120))  # Box, Text colours
                        if self.cursorTouching != ["TOGGLE", script[2]]:
                            if self.playSounds:
                                pygame.mixer.Sound.play(self.menuSounds[3])  # menu scroll
                        self.cursorTouching = ["TOGGLE", script[2]]

                    elif script[0] == "OPTIONS":
                        colours = ((2, 10, 75), (236, 239, 26))
                        self.cursorTouching = ["OPTIONS", script[2]]

            else:
                if buttonScripts[i] == "":  # Check if it is an ordinary button
                    if self.cursorTouching == ["CREATEFILE", options[i][0]]:  # clear touching if no longer touching
                        self.cursorTouching = [None]
                else:  # Run the button's script
                    script = buttonScripts[i]
                    if script[0] == "TOGGLE":
                        if script[1] == 1:
                            colours = ((72, 10, 5), (240, 240, 240))  # Box, Text colours
                            pygame.draw.rect(surface, (234, 79, 18), (
                                optionBox[0] - self.uiBoxCalculations[9], optionBox[1] - self.uiBoxCalculations[9],
                                optionBox[2] + self.uiBoxCalculations[9] * 2,
                                optionBox[3] + self.uiBoxCalculations[9] * 2))
                        if self.cursorTouching == ["TOGGLE", script[2]]:  # clear touching if no longer touching
                            self.cursorTouching = [None]
                    elif script[0] == "OPTIONS":
                        colours = ((2, 10, 75), (240, 240, 240))
                        if self.cursorTouching == ["OPTIONS", script[2]]:  # clear touching if no longer touching
                            self.cursorTouching = [None]

            pygame.draw.rect(surface, colours[0], optionBox)

            text = self.fontMain.render(options[i][0], True, colours[
                1])  # Re-render the text with correct colours depending on mouse collision
            textRect = renderedText[i].get_rect()
            textRect.center = optionBox.center
            surface.blit(text, textRect)

            subText = self.fontSub.render(": " + options[i][1], True, (240, 240, 240))
            subRect = subText.get_rect()
            subRect.topleft = (self.resolution[0] * 0.25 + width / 2 + 6,
                               optionBox.topleft[1])  # x = buton width + 6, y = button y coordinate
            surface.blit(subText, subRect)

    def draw_load_menu(self, surface, mouse_coordinates, access=0):
        # access = 0 loading file mode
        # access = 1 creating new file mode
        self.gradient.fill((6, 38, 5, 220))
        surface.blit(self.gradient, (0, 0))
        uiCollisionRect = self.load_menuCalculations[0]
        if not (uiCollisionRect.collidepoint(mouse_coordinates)):
            self.cursorTouching = [str(access)]  # close the ui

        length = self.load_menuCalculations[1]  # 6 = max number of saves

        for i in range(6):
            saveUI = self.load_menuCalculations[i + 2]

            if saveUI.collidepoint(mouse_coordinates):
                colours = ((13, 76, 12, 200), (220, 220, 220, 140))  # box, line
                if self.cursorTouching != ["SAVE", i]:
                    if self.playSounds:
                        pygame.mixer.Sound.play(self.menuSounds[3])  # menu scroll
                self.cursorTouching = ["SAVE", i]
            else:
                colours = ((6, 38, 5, 140), (220, 220, 220, 80))  # box, line
                if self.cursorTouching == ["SAVE", i]:
                    self.cursorTouching = [None]

            self.saveImage.fill(colours[0])
            self.saveImageLine.fill(colours[1])
            y = self.load_menuYCalculations[i]
            surface.blit(self.saveImage, (self.resolution[0] * 0.1, y))
            surface.blit(self.saveImageLine, (self.resolution[0] * 0.1, y + length - 3))

            # RENDER SAVE TEXT
            savedData = self.savedData[i]

            # Slot number
            text = self.fontSub.render(str(i + 1), True, (240, 240, 240))
            textRect = text.get_rect()
            textRect.topleft = (self.resolution[0] * 0.15, y + length / 3)
            surface.blit(text, textRect)

            if savedData != "corrupted" and savedData != 0:
                # Difficulty
                if savedData[0] == 0:
                    text = "Normal"  # Valour
                elif savedData[0] == 1:
                    text = "Hard"  # Wisdom
                else:
                    text = "Extreme"  # Balance/Vanguard
                text = self.fontSub.render(text, True, (240, 240, 240))
                textRect = text.get_rect()
                textRect.topleft = (self.resolution[0] * 0.3, y + length / 3)
                surface.blit(text, textRect)

                # Level
                level = 0  # Convert exp to level
                if savedData[1] >= 300:
                    level = math.floor(math.sqrt((savedData[1] - 300) / 70) - 1)
                    if level < 0:
                        level = 0
                text = self.fontSub.render("Level " + str(level), True, (240, 240, 240))
                textRect = text.get_rect()
                textRect.topleft = (self.resolution[0] * 0.2, y + length / 3)
                surface.blit(text, textRect)

                # Money
                text = self.fontSub.render("Money " + str(savedData[2]), True, (240, 240, 240))
                textRect = text.get_rect()
                textRect.topleft = (self.resolution[0] * 0.4, y + length / 3)
                surface.blit(text, textRect)

                # Ship Type
                if savedData[3] == 0:
                    text = "Vanguard"  # Valour
                elif savedData[3] == 1:
                    text = "Engineer"  # Wisdom
                elif savedData[3] == 2:
                    text = "Stealth"  # Balance/Vanguard
                else:
                    text = "Recruit"  # New save
                text = self.fontSub.render(text, True, (240, 240, 240))
                textRect = text.get_rect()
                textRect.topright = (self.resolution[0] * 0.89, y + length * (10 / 72))
                surface.blit(text, textRect)

                # Emblems
                if savedData[4][0] != -1:
                    emblem1 = self.emblems[savedData[4][0]]
                    emblem1Rect = emblem1.get_rect()
                    emblem1Rect.topleft = (self.resolution[0] * 0.7, y + length / 7)
                    surface.blit(emblem1, emblem1Rect)

                if savedData[4][1] != -1:
                    emblem2 = self.emblems[savedData[4][1]]
                    emblem2Rect = emblem2.get_rect()
                    emblem2Rect.topleft = (self.resolution[0] * 0.75, y + length / 7)
                    surface.blit(emblem2, emblem2Rect)

                # Current Chapter
                text = self.fontSub.render("Ch " + str(savedData[6]), True, (240, 240, 240))
                textRect = text.get_rect()
                textRect.bottomright = (self.resolution[0] * 0.89, y + length * (62 / 72))
                surface.blit(text, textRect)

            else:
                if savedData == 0:
                    savedData = "NO DATA"
                text = self.fontSub.render(savedData.upper(), True, (240, 240, 240))
                textRect = text.get_rect()
                textRect.topleft = (self.resolution[0] * 0.3, y + length / 3)
                surface.blit(text, textRect)

    def handle_input(self):
        if self.cursorTouching[0] == "0":  # close the ui
            self.instance = "main screen"
            if self.playSounds:
                pygame.mixer.Sound.play(self.menuSounds[1])  # back

            resolution = self.supported_resolutions[self.selected_resolution]
            if resolution == "900x450":
                resolution = (900, 450)
            elif resolution == "1280x720":
                resolution = (1280, 720)
            elif resolution == "1600x900":
                resolution = (1600, 900)
            if self.resolution != resolution:
                self.resolution = resolution
                surface = pygame.display.set_mode(resolution)
                self.resize_assets()

        elif self.cursorTouching[0] == "1":  # go to self.instance new game
            self.instance = "newGame"
            if self.playSounds:
                pygame.mixer.Sound.play(self.menuSounds[1])  # back

        elif self.cursorTouching[0] == "NEW GAME":
            self.instance = "newGame"
            if self.playSounds:
                pygame.mixer.Sound.play(self.menuSounds[2])  # open

        elif self.cursorTouching[0] == "CREATEFILE":
            if self.instance != "confirm":
                self.instance = "createFile"
                self.fileType = self.cursorTouching[1]

                if self.playSounds:
                    pygame.mixer.Sound.play(self.menuSounds[4])  # select

            elif self.instance == "confirm":
                if self.cursorTouching[1] == "Yes":
                    newSave = open(
                        filePath.setPath(filePath.getRootFolder(2), ["data", "saves", "save" + str((self.saveSlot + 1)) + ".txt"]),
                        "w+")  # Create new save or overwrite file
                    if self.fileType == "Normal":
                        difficulty = "0"
                    elif self.fileType == "Hard":
                        difficulty = "1"
                    else:
                        difficulty = "2"
                    self.playerData = [int(difficulty),
                                       0,
                                       0, -
                                       1,
                                       [-1, -1],
                                       [],
                                       0,
                                       {
                                           "equipped techniques": [""],
                                           "equipped talents": ["Surge"],
                                           "technique deck": ["Surge"]
                                        }]  # Store the player's save data to be used on launch
                    newSave.write(json.dumps(self.playerData))
                    newSave.close()
                    # difficulty, level, money, shipType, emblems, items, current chapter
                    self.instance = "startGame"
                    self.clock = 0  # Reset the clock

                    if self.playSounds:
                        pygame.mixer.Sound.play(self.menuSounds[4])  # select

                elif self.cursorTouching[1] == "No":
                    self.instance = "createFile"

                    if self.playSounds:
                        pygame.mixer.Sound.play(self.menuSounds[1])  # back

        elif self.cursorTouching[0] == "LOAD":
            self.instance = "load"
            if self.playSounds:
                pygame.mixer.Sound.play(self.menuSounds[2])  # open

        elif self.cursorTouching[0] == "SAVE":
            if self.instance == "createFile":
                if self.savedData[self.cursorTouching[1]] == 0:  # If an empty save
                    self.createTextOption = "(Start a new save and begin your adventure.)"
                else:
                    self.createTextOption = "(Are you sure you want to overwrite your save file?)"
                self.instance = "confirm"
                self.saveSlot = self.cursorTouching[1]
                if self.playSounds:
                    pygame.mixer.Sound.play(self.menuSounds[4])  # select

            elif self.instance == "load":
                self.playerData = self.savedData[self.cursorTouching[1]]
                if not (self.playerData == 0 or self.playerData == "corrupted"):  # check if the save is loadable
                    self.instance = "startGame"
                    self.clock = 0  # Reset the clock
                    if self.playSounds:
                        pygame.mixer.Sound.play(self.menuSounds[4])  # select
                else:
                    if self.playSounds:
                        pygame.mixer.Sound.play(self.menuSounds[0])  # error

        elif self.cursorTouching[0] == "CONFIG":
            self.instance = "config"
            if self.playSounds:
                pygame.mixer.Sound.play(self.menuSounds[2])  # open

        elif self.cursorTouching[0] == "TOGGLE":
            if self.cursorTouching[1] == "playSounds":
                if self.playSounds == 1:
                    self.playSounds = 0
                else:
                    self.playSounds = 1
                if self.playSounds:
                    pygame.mixer.Sound.play(self.menuSounds[4])  # select

            elif self.cursorTouching[1] == "playMusic":
                if self.playMusic == 1:
                    self.playMusic = 0
                    pygame.mixer.music.pause()
                else:
                    self.playMusic = 1
                    pygame.mixer.music.unpause()
                if self.playSounds:
                    pygame.mixer.Sound.play(self.menuSounds[4])  # select

            elif self.cursorTouching[1] == "customCursor":
                if len(self.gamePads) == 0:
                    if self.customCursor == 1:
                        self.customCursor = 0
                        pygame.mouse.set_visible(True)
                    else:
                        self.customCursor = 1
                        pygame.mouse.set_visible(False)
                    if self.playSounds:
                        pygame.mixer.Sound.play(self.menuSounds[4])  # select
                else:
                    pygame.mixer.Sound.play(self.menuSounds[0])  # error

        elif self.cursorTouching[0] == "OPTIONS":
            if self.cursorTouching[1] == "selectResolution":
                self.selected_resolution += 1
                self.selected_resolution %= 3
                if self.playSounds:
                    pygame.mixer.Sound.play(self.menuSounds[4])  # select
