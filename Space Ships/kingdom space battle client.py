import pygame
import os, json, math
from lib import gameEngine, interface #Needed game scripts

def loadConfig(filePath):
    try:
        config = open(filePath).readlines()
        config = [x.strip() for x in config]
        dicte = "{"
        for i in range(len(config)):
            dicte += config[i]+','
        dicte = dicte[:-1]
        dicte += "}"
        config = json.loads(dicte)
        return config
    except:
        return 0 #loading error

def getRootFolder(retracts=1):
    #retracts is how many times it goes up the file path branch
    path = __file__
    if "\\" in path: #Checks if device uses '\' or '/' to navigate folders
        key = "\\"
    else:
        key = "/"
    path = path.split(key)
    for i in range(retracts):
        path.pop()
    path = key.join(path)
    return path

def setPath(path, pathList):
    if "\\" in path: #Checks if device uses '\' or '/' to navigate folders
        key = "\\"
    else:
        key = "/"
    path = path.split(key)
    for i in range(len(pathList)):
        path.append(pathList[i])
    path = key.join(path)
    return path

class application:

    def __init__(self, dimensions, debug=False, SERVER_IP="192.168.0.2", SERVER_PORT=8080):
        self.SERVER_IP = SERVER_IP
        self.SERVER_PORT = SERVER_PORT
        self.debug = debug
        pygame.mixer.pre_init(44100, -16, 1, 512)
        pygame.init()
        pygame.mouse.set_visible(False)
        self.dimensions = dimensions
        self.surface = pygame.display.set_mode(dimensions)
        pygame.display.set_caption("Kingdom Space Battle")
        
        self.path = getRootFolder()
        
        self.fontMain = pygame.font.Font(setPath(self.path,["assets","fonts","Coda-Regular.ttf"]), 24)
        self.fontSub = pygame.font.Font(setPath(self.path,["assets","fonts","Coda-Regular.ttf"]), 20)

        self.menuSounds = [
            pygame.mixer.Sound(setPath(self.path,["assets","sounds","system sound effects","error.wav"])),
            pygame.mixer.Sound(setPath(self.path,["assets","sounds","system sound effects","menu back.wav"])),
            pygame.mixer.Sound(setPath(self.path,["assets","sounds","system sound effects","menu open.wav"])),
            pygame.mixer.Sound(setPath(self.path,["assets","sounds","system sound effects","menu scroll.wav"])),
            pygame.mixer.Sound(setPath(self.path,["assets","sounds","system sound effects","select.wav"])),
        ]

        menuMusic = pygame.mixer.music.load(setPath(self.path,["assets","sounds","music","kh3-Dearly Beloved.mp3"]))
        pygame.mixer.music.play(-1)
        
        icon = pygame.image.load(setPath(self.path,["assets","title screen","icon.png"]))
        pygame.display.set_icon(icon)

        self.emblems = [
            pygame.image.load(setPath(self.path,["assets","player","emblems","vanguard.png"])),
            pygame.image.load(setPath(self.path,["assets","player","emblems","engineer.png"])),
            pygame.image.load(setPath(self.path,["assets","player","emblems","stealth.png"])),
        ]
        
        for i in range(len(self.emblems)): #Scale images
            self.emblems[i] = pygame.transform.scale(self.emblems[i], self.dimensions)
        
        self.controls = {"up":[pygame.K_w], "left":[pygame.K_a], "right":[pygame.K_d], "down":[pygame.K_s],
                         "SQUARE":[pygame.K_j], "CIRCLE":[pygame.K_l,1], "CROSS":[pygame.K_k,0], "TRIANGLE":[pygame.K_i,3],
                         "start":[pygame.K_p,7], "home":[pygame.K_ESCAPE,6],
                         "L1":[pygame.K_q,4], "R1":[pygame.K_e,5]}

        self.playSounds = 1
        self.playMusic = 1
        self.customCursor = 1

        self.startUpAnimation()
        
        self.mainMenu()

    def mainMenu(self):
        background = pygame.image.load(setPath(self.path,["assets","title screen","overlay.png"]))
        background = pygame.transform.scale(background, self.dimensions)
        
        cursor = pygame.image.load(setPath(self.path,["assets","background","cursor.png"]))
        cursor = pygame.transform.scale(cursor, (40,40))

        self.cursorTouching = [None]

        self.instance = "main screen" #Controls which UI is loaded

        self.savedData = self.loadSaves()

        #Calculations needed for graph coordinates
        boxSpace = self.dimensions[1]/3 - 110
        boxShift = (boxSpace - 3*35)/2 +self.dimensions[1]/3 +70
        boxShift2 = (boxSpace - 2*35)/2 +self.dimensions[1]/3 +70
        #i*45+boxShift  #Box Widths = 168, 242, 119

        graph = {
            "NEW GAME":{"up":"CONFIG","down":"LOAD","value":(self.dimensions[0]-200, self.dimensions[1]-4.6*self.dimensions[1]/20 +5),"next":"Normal","previous":""}, #Controls where the controller should take the cursor
            "LOAD":{"up":"NEW GAME","down":"CONFIG","value":(self.dimensions[0]-200, self.dimensions[1]-3.2*self.dimensions[1]/20 +5),"next":"save1","previous":""},
            "CONFIG":{"up":"LOAD","down":"NEW GAME","value":(self.dimensions[0]-200, self.dimensions[1]-1.8*self.dimensions[1]/20 +5),"next":"Sound","previous":""},
            
            "Normal":{"up":"Extreme","down":"Hard","value":(self.dimensions[0]*0.25+75, boxShift),"next":"save1","previous":"NEW GAME"},
            "Hard":{"up":"Normal","down":"Extreme","value":(self.dimensions[0]*0.25+75, 45+boxShift),"next":"save1","previous":"NEW GAME"},
            "Extreme":{"up":"Hard","down":"Normal","value":(self.dimensions[0]*0.25+75, 90+boxShift),"next":"save1","previous":"NEW GAME"},

            "save1":{"up":"save6","down":"save2","value":(self.dimensions[0]*0.12, self.dimensions[1]*0.25),"next":"Yes","previous":""},
            "save2":{"up":"save1","down":"save3","value":(self.dimensions[0]*0.12, self.dimensions[1]*0.35),"next":"Yes","previous":""},
            "save3":{"up":"save2","down":"save4","value":(self.dimensions[0]*0.12, self.dimensions[1]*0.45),"next":"Yes","previous":""},
            "save4":{"up":"save3","down":"save5","value":(self.dimensions[0]*0.12, self.dimensions[1]*0.55),"next":"Yes","previous":""},
            "save5":{"up":"save4","down":"save6","value":(self.dimensions[0]*0.12, self.dimensions[1]*0.65),"next":"Yes","previous":""},
            "save6":{"up":"save5","down":"save1","value":(self.dimensions[0]*0.12, self.dimensions[1]*0.75),"next":"Yes","previous":""},

            "Sound":{"up":"Custom Cursor","down":"Music","value":(self.dimensions[0]*0.25+112, boxShift),"next":"Sound","previous":"CONFIG"},
            "Music":{"up":"Sound","down":"Custom Cursor","value":(self.dimensions[0]*0.25+112, 45+boxShift),"next":"Music","previous":"CONFIG"},
            "Custom Cursor":{"up":"Music","down":"Sound","value":(self.dimensions[0]*0.25+112, 90+boxShift),"next":"Custom Cursor","previous":"CONFIG"},

            "Yes":{"up":"No","down":"No","value":(self.dimensions[0]*0.25+56.5, boxShift2),"next":"","previous":""},
            "No":{"up":"Yes","down":"Yes","value":(self.dimensions[0]*0.25+56.5, 45+boxShift2),"next":"","previous":""},
        }
        currentNode = "NEW GAME"

        #Transition
        for i in range(63):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

            self.drawMainOption(4.6, (0,0), "NEW GAME")
            self.drawMainOption(3.2, (0,0), "LOAD")
            self.drawMainOption(1.8, (0,0), "CONFIG")

            self.surface.blit(background, (0,0))
                    
            gradient = pygame.Surface(self.dimensions, pygame.SRCALPHA)
            gradient.fill((255,255,255,249-i*3))
            self.surface.blit(gradient, (0,0))
            pygame.display.update()
            pygame.time.delay(16)
            
        if self.customCursor == 1:
            pygame.mouse.set_visible(False)
        else:
            pygame.mouse.set_visible(True)

        #Test the gamepad
        self.gamePads = []
        for i in range(0, pygame.joystick.get_count()): 
            self.gamePads.append(pygame.joystick.Joystick(i))
            self.gamePads[-1].init()
            if self.debug:
                print("Detected gamepad '",self.gamePads[-1].get_name(),"'")
            
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                #Test the gamepad
                if event.type == pygame.JOYBUTTONDOWN:
                    if self.debug:
                        print("button:",event.button)
                    if event.button == 0: #Advance button
                        destination = graph[currentNode]["next"]
                        if destination != "":
                            previousNode = currentNode
                            if previousNode != destination: #Prevents loops
                                currentNode = destination
                                graph[currentNode]["previous"] = previousNode
                                startNode = graph[currentNode]["down"]
                                while startNode != currentNode: #Set all the options previous settings
                                    graph[startNode]["previous"] = previousNode
                                    startNode = graph[startNode]["down"]
                                if previousNode == "LOAD":
                                    for i in range(6):
                                        graph["save"+str(i+1)]["next"] = ""
                                elif graph[previousNode]["previous"] == "NEW GAME":
                                    for i in range(6):
                                        graph["save"+str(i+1)]["next"] = "Yes"
                        elif currentNode == "No":
                            currentNode = graph[currentNode]["previous"]
                        self.handleInput()
                        if self.debug:
                            print("option:",currentNode)
                        
                    if event.button == 1:
                        if graph[currentNode]["previous"] != "":
                            x,y = 0,0
                            currentNode = graph[currentNode]["previous"]
                            if currentNode == "NEW GAME" or currentNode == "LOAD" or currentNode == "CONFIG":
                                self.cursorTouching[0] = "0"
                            elif graph[currentNode]["next"][:2] == "sa":
                                self.cursorTouching[0] = "1"
                            elif currentNode[:2] == "sa":
                                self.cursorTouching = ["CREATEFILE", "No"]
                            else:
                                self.cursorTouching[0] = "0"
                            self.handleInput()
                        else:
                            pygame.mixer.Sound.play(self.menuSounds[1]) #back
                            
                        if self.debug:
                            print("option:",currentNode)

                if event.type == pygame.JOYHATMOTION:
                    dpad = self.gamePads[0].get_hat(0)
                    if self.debug:
                        print("dpad:",dpad)
                    if dpad[1] == 1:
                        currentNode = graph[currentNode]["up"]
                    elif dpad[1] == -1:
                        currentNode = graph[currentNode]["down"]
                        
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if len(self.gamePads) == 0:
                        self.handleInput()
                                
            if self.instance == "startGame":
                break
            
            self.surface.fill((255,255,255)) #Make screen blank (white)
            self.surface.blit(background, (0,0)) #Title

            if len(self.gamePads) > 0:
                x,y = graph[currentNode]["value"]
                y +=4 # move y down slightlty
            else:
                x,y = pygame.mouse.get_pos() #Get mouse coordinates

            if self.instance == "main screen":
                self.drawMainOption(4.6, (x,y), "NEW GAME")
                self.drawMainOption(3.2, (x,y), "LOAD")
                self.drawMainOption(1.8, (x,y), "CONFIG")
                
            else: #Render the gui but prevent selection and collision
                self.drawMainOption(4.6, (0,0), "NEW GAME")
                self.drawMainOption(3.2, (0,0), "LOAD")
                self.drawMainOption(1.8, (0,0), "CONFIG")

            #Instances
            if self.instance == "newGame":
                self.drawUIBOX((x,y), "Select a game difficulty level.", "(The difficulty can not be changed.)",
                    [
                    ("Normal","Standard difficulty, recommended for new players."),
                    ("Hard","Enemy stats are increased to x1.3."),
                    ("Extreme","Enemy stats are increased to x1.5, damage increased to x1.25, EXP gain decreased to x0.8.")
                ])
                
            elif self.instance == "createFile":
                self.loadMenu((x,y), 1)
                
            elif self.instance == "load":
                self.loadMenu((x,y))

            elif self.instance == "confirm":
                self.drawUIBOX((x,y), "CREATE A NEW SAVE", self.createTextOption,
                    [
                    ("Yes","Begin your new save with "+self.fileType.upper()+" difficulty."),
                    ("No","Return to save menu."),
                ])
                
            elif self.instance == "config":
                self.drawUIBOX((x,y), "Configure your options.", "(These can be changed in-game.)",
                    [
                    ("Sound","Toggle if sound effects are played."),
                    ("Music","Toggle if music is played."),
                    ("Custom Cursor","Toggle between custom cursor and your device's cursor.")
                ],
                    [
                    ("TOGGLE", self.playSounds, "playSounds"),
                    ("TOGGLE", self.playMusic, "playMusic"),
                    ("TOGGLE", self.customCursor, "customCursor"),
                ])

            if self.customCursor: #Render custom mouse if the option is on
                cursorRect = cursor.get_rect()
                cursorRect.center = (x,y)
                self.surface.blit(cursor, cursorRect) 
            
            pygame.display.update()
            pygame.time.delay(16)
            
        self.launchGame() #Launch the game once the main menu has been exited.
        
    def drawMainOption(self, y, mouse_coordinates, text="TEST"):
        optionsRect = (self.dimensions[0]*0.4, self.dimensions[1]/20) #Constant for ui sizes 

        y = self.dimensions[1] - y*optionsRect[1] #Align by multiplier

        #Gradient Colour Surfaces
        rectangleSurface = pygame.Surface(optionsRect, pygame.SRCALPHA)
        squareSurface = pygame.Surface((optionsRect[1], optionsRect[1]), pygame.SRCALPHA)
        highlightSurface = pygame.Surface((optionsRect[1]*0.6, optionsRect[1]*0.6), pygame.SRCALPHA)
        lineSurface = pygame.Surface((self.dimensions[0]-30, 3), pygame.SRCALPHA)

        if mouse_coordinates[0] >= 30 and mouse_coordinates[1] > y and mouse_coordinates[1] < (y+optionsRect[1]): #Calculate if touching the mouse pointer
            colours = ((113,169,247,140), (0,0,0,255), (113,169,247,255)) #Rectangle, Square & Line, Hightlight #230,250,252 | 113,169,247 Colour Codes
            textColour = (0,0,0)
            if self.cursorTouching[0] != text:
                if self.playSounds:
                    pygame.mixer.Sound.play(self.menuSounds[3]) #menu scroll
            self.cursorTouching = [text]
        else:
            colours = ((160,160,160,190), (160,160,160,190), (0,0,0,0)) #Rectangle, Square & Line, Highlight
            textColour = (175,175,175)
            if self.cursorTouching[0] == text: #clear touching if no longer touching
                self.cursorTouching = [None]
            
        rectangleSurface.fill(colours[0])
        squareSurface.fill(colours[1])
        highlightSurface.fill(colours[2])
        lineSurface.fill(colours[1])

        self.surface.blit(rectangleSurface, (self.dimensions[0]+1-optionsRect[0], y))
        self.surface.blit(squareSurface, (30, y))
        self.surface.blit(highlightSurface, (30+optionsRect[1]*0.2, y+optionsRect[1]*0.2))
        self.surface.blit(lineSurface, (30, y+optionsRect[1]-3))

        text = self.fontMain.render(text, True, textColour)
        text_rect = text.get_rect()
        text_rect.topleft = (30+optionsRect[1]+10, y)
        self.surface.blit(text, text_rect)
        
    def drawUIBOX(self, mouse_coordinates, title="Select a game difficulty.", text="(Select an option.)", options=[("Test1","Hover on me."), ("Test2","Hover on me.")], buttonScripts=[]):
        iterations = len(options)-len(buttonScripts) #Load button scripts
        for i in range(iterations):
            buttonScripts.append("")

        #Draw the ui box
        transparentBackGround = pygame.Surface(self.dimensions, pygame.SRCALPHA)
        transparentBackGround.fill((0,0,0,200))
        uiBox = pygame.Surface((self.dimensions[0], self.dimensions[1]/3), pygame.SRCALPHA)
        uiBox.fill((0,0,0,170))
        self.surface.blit(transparentBackGround, (0,0))
        self.surface.blit(uiBox, (0,self.dimensions[1]/3))
        pygame.draw.line(self.surface, (168,149,229), (0, self.dimensions[1]/3-5), (self.dimensions[0], self.dimensions[1]/3 -5), 7) #Top border
        pygame.draw.line(self.surface, (168,149,229), (0, 2*self.dimensions[1]/3), (self.dimensions[0], 2*self.dimensions[1]/3), 7) #Bottom border

        #Check if touching outside the menu
        if mouse_coordinates[1] < self.dimensions[1]/3 -7 or mouse_coordinates[1] > 2*self.dimensions[1]/3 + 7:
            self.cursorTouching = ["0"] #close the ui
        
        text = self.fontMain.render(text, True, (236,239,26)) #Information text
        title = self.fontMain.render(title, True, (240,240,240)) #Tile text
        
        textRect = text.get_rect()  #Information text box
        textRect.center = (self.dimensions[0]/2, 2*self.dimensions[1]/3 - 25)
        self.surface.blit(text, textRect) #Information text render
        titleRect = title.get_rect()
        titleRect.center = (self.dimensions[0]/2, self.dimensions[1]/3 + 30)
        self.surface.blit(title, titleRect) #Information text render

        longestText = 0
        renderedText = []
        for i in range (len(options)): #Find the option with the longest text length
            renderedText.append(self.fontMain.render(options[i][0], True, (240,240,240)))
            length = renderedText[i].get_rect()[2] #2 = width of the text
            if length > longestText:
                longestText = length
        #Set width of the button using the longest length so that all buttons are the same width
        width = longestText + 80 #40 on each side
        boxSpace = self.dimensions[1]/3 - 110 #The vertical length of space the buttons will be placed in
        numOfOptions = len(options)
        boxShift = (boxSpace - numOfOptions*35)/2 +self.dimensions[1]/3 +70 # Creates equal gap between title and the text
        for i in range(numOfOptions):
            colours = ((10,5,25), (120,120,120)) #Box, Text colours
            
            optionBox = pygame.Rect(0,0,width,35) #x,y,width,length
            optionBox.center = (self.dimensions[0]*0.25, i*45+boxShift)

            if optionBox.collidepoint(mouse_coordinates): #change colours if collinding with mouse
                
                if buttonScripts[i] == "": #Check if it is an ordinary button
                    colours = ((56,9,5), (240,240,240)) #Box, Text colours
                    pygame.draw.rect(self.surface, (168,24,11), (optionBox[0]-3,optionBox[1]-3,optionBox[2]+6,optionBox[3]+6)) #Highlighted border
                    if self.cursorTouching != ["CREATEFILE",options[i][0]]:
                        if self.playSounds:
                            pygame.mixer.Sound.play(self.menuSounds[3]) #menu scroll
                    self.cursorTouching = ["CREATEFILE",options[i][0]]
                    
                else: #Run the button's script
                    script = buttonScripts[i]
                    if script[0] == "TOGGLE":
                        if script[1] == 1:
                            colours = ((72,10,5), (240,240,240)) #Box, Text colours
                            pygame.draw.rect(self.surface, (234,79,18), (optionBox[0]-3,optionBox[1]-3,optionBox[2]+6,optionBox[3]+6))
                        else:
                            if self.cursorTouching != ["TOGGLE", script[2]]:
                                colours = ((10,5,25), (120,120,120)) #Box, Text colours
                        if self.cursorTouching != ["TOGGLE", script[2]]:
                            if self.playSounds:
                                pygame.mixer.Sound.play(self.menuSounds[3]) #menu scroll
                        self.cursorTouching = ["TOGGLE", script[2]]
                    
            else:
                if buttonScripts[i] == "": #Check if it is an ordinary button
                    if self.cursorTouching == ["CREATEFILE",options[i][0]]: #clear touching if no longer touching
                        self.cursorTouching = [None]
                else: #Run the button's script
                    script = buttonScripts[i]
                    if script[0] == "TOGGLE":
                        if script[1] == 1:
                            colours = colours = ((72,10,5), (240,240,240)) #Box, Text colours
                            pygame.draw.rect(self.surface, (234,79,18), (optionBox[0]-3,optionBox[1]-3,optionBox[2]+6,optionBox[3]+6))
                        if self.cursorTouching == ["TOGGLE", script[2]]: #clear touching if no longer touching
                            self.cursorTouching = [None]
            
            pygame.draw.rect(self.surface, colours[0], optionBox)

            text = self.fontMain.render(options[i][0], True, colours[1]) #Re-render the text with correct colours depending on mouse collision
            textRect = renderedText[i].get_rect()
            textRect.center = optionBox.center
            self.surface.blit(text, textRect)
            
            subText = self.fontSub.render(": "+options[i][1], True, (240,240,240))
            subRect = subText.get_rect()
            subRect.topleft = (self.dimensions[0]*0.25 +width/2 +6, optionBox.topleft[1]) #x = buton width + 6, y = button y coordinate
            self.surface.blit(subText, subRect)

    def loadSaves(self):
        saves = []
        for i in range(6): #6 = maximum number of saves
            try: #Load save files
                #File formate = [difficulty, level, money, shipType, emblems, items, current chapter]
                saveFile = open(setPath(self.path,["data","saves","save"+str((i+1))+".txt"]), "r").readlines()
                try: #Check if the save is interperatble
                    save = 0
                    savedData = json.loads(saveFile[0])
                    if 0 <= savedData[0] and savedData[0] <= 2: #difficulty
                        if 0 <= savedData[1] and savedData[1] <= 260770: #exp
                            if 0 <= savedData[2] and savedData[2] <= 99999: #money
                                if -1 <= savedData[3] and savedData[3] <= 2: #shipType
                                    if -1 <= savedData[4][0] and savedData[4][0] <= 2 and -1 <= savedData[4][1] and savedData[4][1] <= 2: #emblems
                                        if 0 <= savedData[6] and savedData[6] <= 21: #current chapter
                                            saves.append(savedData)
                                            save = 1
                    if save == 0:
                        saves.append("corrupted")
                        
                except: #Returned save corrupted
                    saves.append("corrupted")
                    
            except: #Skip if save not found
                saves.append(0)
        if self.debug:
            for i in range(len(saves)): print(saves[i])
            print("")
        return saves

    def loadMenu(self, mouse_coordinates, access = 0):
        #access = 0 loading file mode
        #access = 1 creating new file mode
        transparentBackGround = pygame.Surface(self.dimensions, pygame.SRCALPHA)
        transparentBackGround.fill((6,38,5,220))
        self.surface.blit(transparentBackGround,(0,0))
        uiCollisionRect = pygame.Rect(self.dimensions[0]*0.1, self.dimensions[1]*0.2, self.dimensions[0]*0.8, self.dimensions[1]*0.6)
        if not(uiCollisionRect.collidepoint(mouse_coordinates)):
            self.cursorTouching = [str(access)] #close the ui
            
        length = self.dimensions[1]*0.1 #6 = max number of saves
        
        for i in range(6):
            saveImage = pygame.Surface((self.dimensions[0]*0.8, length), pygame.SRCALPHA)
            saveImageLine = pygame.Surface((self.dimensions[0]*0.8, 3), pygame.SRCALPHA)
            saveUI = pygame.Rect(self.dimensions[0]*0.1, self.dimensions[1]*0.2 +i*length, self.dimensions[0]*0.8, length)
            
            if saveUI.collidepoint(mouse_coordinates):
                colours = ((13,76,12,200), (220,220,220,140)) #box, line
                if self.cursorTouching != ["SAVE", i]:
                    if self.playSounds:
                        pygame.mixer.Sound.play(self.menuSounds[3]) #menu scroll
                self.cursorTouching = ["SAVE",i]
            else:
                colours = ((6,38,5,140), (220,220,220,80)) #box, line
                if self.cursorTouching == ["SAVE", i]:
                    self.cursorTouching = [None]
                    
            saveImage.fill(colours[0])
            saveImageLine.fill(colours[1])
            y = self.dimensions[1]*0.2+i*length
            self.surface.blit(saveImage, (self.dimensions[0]*0.1, y))
            self.surface.blit(saveImageLine, (self.dimensions[0]*0.1, y+length-3))

            #RENDER SAVE TEXT
            savedData = self.savedData[i]

            #Slot number
            text = self.fontSub.render(str(i+1), True, (240,240,240))
            textRect = text.get_rect()
            textRect.topleft = (self.dimensions[0]*0.15, y+length/3)
            self.surface.blit(text, textRect)
            
            if savedData != "corrupted" and savedData != 0:
                #Difficulty
                if savedData[0] == 0: 
                    text = "Normal" #Valour
                elif savedData[0] == 1:
                    text = "Hard" #Wisdom
                else:
                    text = "Extreme" #Balance/Vanguard
                text = self.fontSub.render(text, True, (240,240,240))
                textRect = text.get_rect()
                textRect.topleft = (self.dimensions[0]*0.3, y+length/3)
                self.surface.blit(text, textRect)
                
                #Level
                level = 0  #Convert exp to level
                if savedData[1] >= 300:
                    level = math.floor(math.sqrt((savedData[1]-300)/70)-1)
                    if level < 0:
                        level = 0
                text = self.fontSub.render("Level "+str(level), True, (240,240,240))
                textRect = text.get_rect()
                textRect.topleft = (self.dimensions[0]*0.2, y+length/3)
                self.surface.blit(text, textRect)

                #Money
                text = self.fontSub.render("Money "+str(savedData[2]), True, (240,240,240))
                textRect = text.get_rect()
                textRect.topleft = (self.dimensions[0]*0.4, y+length/3)
                self.surface.blit(text, textRect)

                #Ship Type
                if savedData[3] == 0: 
                    text = "Vanguard" #Valour
                elif savedData[3] == 1:
                    text = "Engineer" #Wisdom
                elif savedData[3] == 2:
                    text = "Stealth" #Balance/Vanguard
                else:
                    text = "Recruit" #New save
                text = self.fontSub.render(text, True, (240,240,240))
                textRect = text.get_rect()
                textRect.topright = (self.dimensions[0]*0.89, y+length*(10/72))
                self.surface.blit(text, textRect)

                #Emblems
                if savedData[4][0] != -1:
                    emblem1 = self.emblems[savedData[4][0]]
                    emblem1Rect = emblem1.get_rect()
                    emblem1Rect.topleft = (self.dimensions[0]*0.7, y+length/7)
                    self.surface.blit(emblem1, emblem1Rect)
                    
                if savedData[4][1] != -1:
                    emblem2 = self.emblems[savedData[4][1]]
                    emblem2Rect = emblem2.get_rect()
                    emblem2Rect.topleft = (self.dimensions[0]*0.75, y+length/7)
                    self.surface.blit(emblem2, emblem2Rect)

                #Current Chapter
                text = self.fontSub.render("Ch "+str(savedData[6]), True, (240,240,240))
                textRect = text.get_rect()
                textRect.bottomright = (self.dimensions[0]*0.89, y+length*(62/72))
                self.surface.blit(text, textRect)
                
            else:
                if savedData == 0:
                    savedData = "NO DATA"
                text = self.fontSub.render(savedData.upper(), True, (240,240,240))
                textRect = text.get_rect()
                textRect.topleft = (self.dimensions[0]*0.3, y+length/3)
                self.surface.blit(text, textRect)

    def handleInput(self):
        if self.cursorTouching[0] == "0": #close the ui
            self.instance = "main screen"
            if self.playSounds:
                pygame.mixer.Sound.play(self.menuSounds[1]) #back
                                
        elif self.cursorTouching[0] == "1": #go to self.instance new game
            self.instance = "newGame"
            if self.playSounds:
                pygame.mixer.Sound.play(self.menuSounds[1]) #back

        elif self.cursorTouching[0] == "NEW GAME":
            self.instance = "newGame"
            if self.playSounds:
                pygame.mixer.Sound.play(self.menuSounds[2]) #open

        elif self.cursorTouching[0] == "CREATEFILE":
            if self.instance != "confirm":
                self.instance = "createFile"
                self.fileType = self.cursorTouching[1]

                if self.playSounds:
                        pygame.mixer.Sound.play(self.menuSounds[4]) #select
                        
            elif self.instance == "confirm":
                if self.cursorTouching[1] == "Yes":
                    newSave = open(setPath(self.path,["data","saves","save"+str((self.saveSlot+1))+".txt"]), "w+") #Create new save or overwrite file
                    if self.fileType == "Normal":
                        difficulty = "0"
                    elif self.fileType == "Hard":
                        difficulty = "1"
                    else:
                        difficulty = "2"
                    self.playerData = [int(difficulty), 0, 0, -1, [-1,-1], [], 0, {"commands":["Surge"]}] #Store the player's save data to be used on launch
                    newSave.write(json.dumps(self.playerData))
                    newSave.close()
                    #difficulty, level, money, shipType, emblems, items, current chapter
                    self.instance = "startGame"

                    if self.playSounds:
                        pygame.mixer.Sound.play(self.menuSounds[4]) #select
                                
                elif self.cursorTouching[1] == "No":
                    self.instance = "createFile"

                    if self.playSounds:
                        pygame.mixer.Sound.play(self.menuSounds[1]) #back

        elif self.cursorTouching[0] == "LOAD":
            self.instance = "load"
            if self.playSounds:
                pygame.mixer.Sound.play(self.menuSounds[2]) #open
                                
        elif self.cursorTouching[0] == "SAVE":
            if self.instance == "createFile":
                if self.savedData[self.cursorTouching[1]] == 0: #If an empty save
                    self.createTextOption = "(Start a new save and begin your adventure.)"
                else:
                    self.createTextOption = "(Are you sure you want to overwrite your save file?)"
                self.instance = "confirm"
                self.saveSlot = self.cursorTouching[1]
                if self.playSounds:
                    pygame.mixer.Sound.play(self.menuSounds[4]) #select
                                
            elif self.instance == "load":
                self.playerData = self.savedData[self.cursorTouching[1]]
                if not(self.playerData == 0 or self.playerData == "corrupted"):#check if the save is loadable
                    self.instance = "startGame"
                    if self.playSounds:
                        pygame.mixer.Sound.play(self.menuSounds[4]) #select
                else:
                    if self.playSounds:
                        pygame.mixer.Sound.play(self.menuSounds[0]) #error
                                
        elif self.cursorTouching[0] == "CONFIG":
            self.instance = "config"
            if self.playSounds:
                pygame.mixer.Sound.play(self.menuSounds[2]) #open

        elif self.cursorTouching[0] == "TOGGLE":
            if self.cursorTouching[1] == "playSounds":
                if self.playSounds == 1:
                    self.playSounds = 0
                else:
                    self.playSounds = 1
                if self.playSounds:
                    pygame.mixer.Sound.play(self.menuSounds[4]) #select
                                
            elif self.cursorTouching[1] == "playMusic":
                if self.playMusic == 1:
                    self.playMusic = 0
                    pygame.mixer.music.pause()
                else:
                    self.playMusic = 1
                    pygame.mixer.music.unpause()
                if self.playSounds:
                    pygame.mixer.Sound.play(self.menuSounds[4]) #select
                            
            elif self.cursorTouching[1] == "customCursor":
                if len(self.gamePads) == 0:
                    if self.customCursor == 1:
                        self.customCursor = 0
                        pygame.mouse.set_visible(True)
                    else:
                        self.customCursor = 1
                        pygame.mouse.set_visible(False)
                    if self.playSounds:
                        pygame.mixer.Sound.play(self.menuSounds[4]) #select
                else:
                    pygame.mixer.Sound.play(self.menuSounds[0]) #error
                    
    def startUpAnimation(self):
        #Startup animation
        startupImage = pygame.image.load(setPath(self.path,["assets","title screen","logo.png"])).convert()
        startupImage = pygame.transform.scale(startupImage, self.dimensions)
        startupRect = startupImage.get_rect()
        startupRect.center = (round(self.dimensions[0]/2), round(self.dimensions[1]/2))

        for i in range (152):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    
            self.surface.fill((0,0,0))
            #1.5 seconds
            if i < 75:
                startupImage.set_alpha(i*4+1)
            self.surface.blit(startupImage, startupRect)
            pygame.display.update()
            pygame.time.delay(16)

        #Transition
        for i in range(60):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    
            gradient = pygame.Surface(self.dimensions, pygame.SRCALPHA)
            gradient.fill((0,0,0,i*4+1))
            self.surface.blit(gradient, (0,0))
            pygame.display.update()
            pygame.time.delay(16)

    def loadingScreen(self):
        pygame.mixer.music.fadeout(3000)
        for i in range(30):
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    
            gradient = pygame.Surface(self.dimensions, pygame.SRCALPHA)
            gradient.fill((0,0,0,i*8+1))
            self.surface.blit(gradient, (0,0))
            pygame.display.update()
            pygame.time.delay(16)
                   
        text = self.fontMain.render("LOADING", True, (240,240,240))
        textRect = text.get_rect()
        textRect.bottomright = (self.dimensions[0]*0.95, self.dimensions[1]-8)
        self.surface.blit(text, textRect)
        pygame.display.update()
        pygame.time.delay(1000) #Give 1 second waiting time

    def launchGame(self):
        #Fade out the music
        self.loadingScreen()
        engine = gameEngine.engine(self.surface, self.dimensions, self.controls, self.debug, self.SERVER_IP, self.SERVER_PORT)

        #Tutorial Test
        engine.addEntity("npc", {"name":"Tutorial Guide", "colour":(244,86,65),
                                 "speech":(
                                     ["Welcome to the tutorial level!","Each NPC you meet will teach you the basics of the game."],
                                     ["Goodluck and enjoy."])
                                 }, (0,-200,0))
        engine.addEntity("npc", {"name":"Tutorial: Navigation", "colour":(244,86,65),
                                 "speech":(
                                     ["Use the Q and E keys to cycle through the command menu.", "It is the menu located at the bottom right of your screen."],
                                     ["The command menu allows you to perform actions","such as attacking and using items."])
                                 }, (0,-600,0))
        engine.addEntity("npc", {"name":"Tutorial: HUD", "colour":(244,86,65),
                                 "speech":(
                                     ["On the bottom right of your screen there is the health and", "mana bar. The blue mana bar is used when spells are cast."],
                                     ["Upon reaching 0 mana the bar will automatically regenrate.","Both the health and mana bar can be refilled using items."],
                                     ["In the top right corner is your mini map","The minimap will display what town you are currently in."],
                                     ["It will also show nearby enemies, npcs and items."])
                                 }, (0,-1000,0))
        
        #Entity parameters = tag, stats, position, size
        engine.addEntity("player", {"colour":(0,50,0), "savedData":self.playerData,"maxHp":100}, (0,0,-math.pi/2), 35)
        engine.addEntity("location", {"name":"Twilight Zone", "colour":(0,0,0)}, (0,0,0), 300)
        engine.addEntity("npc", {"name":"Twilight Zone", "colour":(0,0,0),"instance":"Station Baracks"}, (0,0,0), 35)
        engine.addEntity("location", {"name":"Olympic City", "colour":(200,150,80)}, (0,-3000,0), 200)
        engine.addEntity("npc", {"name":"Olympic City", "colour":(200,150,80),"instance":"World Hub"}, (0,-3000,0), 35)
        
        #engine.addEntity("npc", {"name":"Bobby Schmack", "colour":(244,86,65), "speech":("This is the test level.", "It is a sandbox where everything in the game is tested." , "move around with WASD and interact with IJKL.")}, (-400,346,0))
        #engine.addEntity("npc", {"name":"Carl", "colour":(66,167,244), "speech":("Hello there!", "I guess I can speak now.")}, (0,-346,0))
        #engine.addEntity("npc", {"name":"Martin", "colour":(76,65,244), "speech":("Did you know that Carl was the first npc created?",)}, (400,346,0))

        #Passive dummies[Twilight Zone]
        engine.addEntity("square", {"colour":(10,30,80)}, (0, -1600, 0))
        engine.addEntity("square", {"colour":(20,30,80)}, (0, -1200, math.pi))
        engine.addEntity("square", {"colour":(30,30,80)}, (0, -800, 0))
        engine.addEntity("square", {"colour":(40,30,80)}, (0, -400, math.pi))
        engine.addEntity("square", {"name":"Dummy-1","colour":(50,30,80)}, (0, 0, 0))
        engine.addEntity("square", {"colour":(60,30,80)}, (0, 400, math.pi))
        engine.addEntity("square", {"colour":(70,30,80)}, (0, 800, 0))
        engine.addEntity("square", {"colour":(80,30,80)}, (0, 1200, math.pi))
        engine.addEntity("square", {"colour":(90,30,80)}, (0, 1600, 0))

        #Swarm[Olympic City]
        engine.addEntity("triangle", {"name":"Swarm","colour":(42,104,193),"hp":14}, (50,-2700,math.pi/4))
        engine.addEntity("triangle", {"name":"Swarm","colour":(42,104,193),"hp":14}, (-50,-2700,math.pi/4)) 
        engine.addEntity("triangle", {"name":"Swarm","colour":(42,104,193),"hp":14}, (200,-2700,math.pi/4)) 
        engine.addEntity("triangle", {"name":"Swarm","colour":(42,104,193),"hp":14}, (-200,-2700,3*math.pi/4))
        engine.addEntity("triangle", {"name":"Swarm","colour":(42,104,193),"hp":14}, (-150,-2650,5*math.pi/4))
        engine.addEntity("triangle", {"name":"Swarm","colour":(42,104,193),"hp":14}, (150,-2650,7*math.pi/4))
        engine.addEntity("triangle", {"name":"Swarm","colour":(42,104,193),"hp":14}, (-100,-2600,5*math.pi/4))
        engine.addEntity("triangle", {"name":"Swarm","colour":(42,104,193),"hp":14}, (100,-2600,7*math.pi/4))

        #Super enemies[Collectibles/Easter Eggs]
        engine.addEntity("triangle", {"name":"Purple Bandit","colour":(22,57,107),"hp":120}, (0,-2650,math.pi/4)) 
        engine.addEntity("triangle", {"name":"Purple Bandit","colour":(160,30,140),"hp":120}, (2600,0,3*math.pi/4))
        engine.addEntity("triangle", {"name":"Purple Bandit","colour":(160,30,140),"hp":120}, (450,2000,7*math.pi/4))

        while True:
            arguments = engine.update()
            if arguments == 0: #Exit adventure mode
                pygame.mouse.set_visible(False)
                self.loadingScreen()
                pygame.mixer.music.play(-1)
                self.mainMenu()
            #pygame.time.delay(16) Engine has built in waiting

#Set constants
config = loadConfig(setPath(getRootFolder(),["config.txt"]))
SERVER_IP = config["SERVER_IP"]
SERVER_PORT = config["SERVER_PORT"]
RESOLUTION = config["RESOLUTION"]
os.environ['SDL_VIDEO_CENTERED'] = '1'
debug = False
game = application(RESOLUTION, debug,  SERVER_IP, SERVER_PORT)

