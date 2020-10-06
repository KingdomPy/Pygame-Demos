import pygame
import math
from lib import objects, interface
import _thread, socket, json #For networking features

#Constants
RETRACTS = 2 #See getRootFolder

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

class engine:
    def __init__(self, surface, dimensions, controls, debug=False, SERVER_IP="192.168.0.2", SERVER_PORT=8080):
        if debug:
            print("Game Engine initiating.")
        self.SERVER_IP = SERVER_IP
        self.SERVER_PORT = SERVER_PORT
        self.debug = debug
        self.surface = surface
        self.dimensions = dimensions
        self.player = None
        self.focus = None
        self.networkType = "Host"
        self.networkSocket = None
        self.connectedAddresses = []
        self.activeAddresses = []
        self.multiplayerEntities = []
        self.entities = []
        self.projectiles = []
        self.animations = []
        self.playerAnimations = ("guard","light dash","barrier","repair")
        self.party = []
        self.instance = "map"
        self.baracksAnimation = [0,0,0]
        self.pausedInstances = ("paused", "interaction", "baracks")
        self.controls = controls
        self.selectedMove = 0
        self.path = getRootFolder(RETRACTS)
        self.immortalEntities = ("location","npc")
        self.entityGroups = {"enemy":("square","triangle"), "ally":("player",)}
        
        #Load assets
        self.menuFont = pygame.font.Font(setPath(self.path,["assets","fonts","Kh2_Menu_Font.ttf"]), 30)
        self.npcFont = pygame.font.Font(setPath(self.path,["assets","fonts","Coda-Regular.ttf"]), 30)
        self.npcNameFont = pygame.font.Font(setPath(self.path,["assets","fonts","Coda-Regular.ttf"]), 27) 
        self.speechBox = pygame.Rect(174+50, self.dimensions[1]- 200, self.dimensions[0]-220-174-50-20, 164)
        self.transRedSurface = pygame.Surface((self.dimensions[0]*0.1375,self.dimensions[1]*0.075), pygame.SRCALPHA)
        self.infoBoxColour = [94,16,8]
        self.transRedSurface.fill(((168,24,11,140)))
        
        #Load required parts of the engine
        self.camera = camera(surface, dimensions, debug)
        self.hud = interface.display(surface, dimensions, debug)

        #Load the first controller as the game's controller
        self.gamePad = None
        if pygame.joystick.get_count() > 0: 
            self.gamePad = pygame.joystick.Joystick(0)
            self.gamePad.init()
            if self.debug:
                print("Detected joystick '",self.gamePad.get_name(),"'")

        #Load menu navigation graph
        self.baracksGraph = {
            "":{"up":"Items","down":"Items"},
            "Items":{"up":"Config","down":"Equipment"},
            "Equipment":{"up":"Items","down":"Abilities"},
            "Abilities":{"up":"Equipment","down":"Customise"},
            "Customise":{"up":"Abilities","down":"Status"},
            "Status":{"up":"Customise","down":"Config"},
            "Config":{"up":"Status","down":"Items"}
        }
        self.baracksOption = [""]
        self.abilityNavigation = [0,0] #Replacing ability navigation 
        self.changeAbility = 0 #Type of ability to be replaced
        
        if self.debug:
            pygame.mouse.set_visible(True)
            print("Game Engine ready.")
        
    def setControls(self, controls):
        self.controls = controls

    def setFocus(self, focus):
        self.focus = focus
        self.camera.setFocus(focus)
        
    def addEntity(self, tag, stats={}, position=(0,0,0), size=30):
        if tag == "player":
            entity = objects.player(tag, stats, position, size, self.dimensions)
            self.setFocus(entity)
            self.player = entity
            self.party.append(self.player)

            #Dummy Test
            '''testSave = [2, 179000, 0, 0, [1, 2], [], 0, {'commands': ['Hyper', 'Missile', 'Repair', 'Teleport', 'Guard']}]
            dummyPlayer = ("player", {"colour":(0,50,0),"name":"Ally Dummy Player","savedData":testSave,"maxHp":100}, (0,0,math.pi/2), 35)
            dummyPlayer = objects.player(dummyPlayer[0],dummyPlayer[1],dummyPlayer[2],dummyPlayer[3])
            self.party.append(dummyPlayer)
            self.entities.append(dummyPlayer)'''
            
        elif tag == "triangle":
            entity = objects.triangle(tag, stats, position, size, self.dimensions)
        elif tag == "square":
            entity = objects.square(tag, stats, position, size, self.dimensions)
        elif tag == "location":
            entity = objects.location(tag, stats, position, size, self.dimensions)
        elif tag == "npc":
            entity = objects.npc(tag, stats, position, size, self.dimensions)
        self.entities.append(entity)

    def runCommand(self, command, data):
        if command == "bullet":
            bullets = []
            for attack in data:
                if attack[0] == "shotgun":
                    bullets.append(objects.bullet(attack[0], attack[1], attack[2], attack[3]))
                    attack[2][2] += 0.12 # Angle
                    bullets.append(objects.bullet(attack[0], attack[1], attack[2], attack[3]))
                    attack[2][2] -= 0.24 #Angle
                    bullets.append(objects.bullet(attack[0], attack[1], attack[2], attack[3]))
                elif attack[0] == "explosion":
                    for i in range(attack[1]):
                        bullets.append(objects.bullet(attack[0], attack[2], attack[3], attack[4]))
                        attack[3][2] += 2*math.pi/attack[1] # Angle
                else:
                    bullets.append(objects.bullet(attack[0], attack[1], attack[2], attack[3]))
                
            for i in range(len(bullets)):
                self.projectiles.append(bullets[i])
                
        elif command == "animation":
            self.animations.append(objects.animation(data[0],data[1],data[2],data[3]))

    def handleInput(self, button):
        if button in self.controls["home"]:
            self.returnToMenu = True

        if self.instance == "map":
            if button in self.controls["down"]: #camera test
                if self.focus == self.player:
                    self.setFocus(self.entities[7]) #Square Ai
                else:
                    self.setFocus(self.player)
                
            if button in self.controls["start"]:
                self.instance = "paused"
                if self.debug:
                    print("INSTANCE:",self.instance)

            if button in self.controls["TRIANGLE"]:
                if self.player.animations[0] == "":
                    self.interactSelected = True
                
            if button in self.controls["CROSS"]:
                option = self.player.commandOptions[self.selectedMove]
                command = self.player.activateCommand(self.selectedMove)
                if command != None:
                    self.runCommand(command[0], command[1])
                elif option == "Magic" or option == "Items" or option == "Drive":
                    self.selectedMove = 0  #Position the navigation to the top

            if button in self.controls["CIRCLE"]:
                self.player.commandOptions = ("Attack","Magic","Items","Drive")
                if self.player.lastSelected != None:
                    self.selectedMove = self.player.lastSelected 

            if button in self.controls["SQUARE"]:
                command = self.player.activateCommand(4) #Dodge/Guard Command
                if command != None:
                    self.runCommand(command[0], command[1])
                
            if button in self.controls["L1"]:
                self.selectedMove = (self.selectedMove-1)%4
                while self.player.commandOptions[self.selectedMove] == "":
                    self.selectedMove = (self.selectedMove-1)%4

            if button in self.controls["R1"]:
                self.selectedMove = (self.selectedMove+1)%4
                while self.player.commandOptions[self.selectedMove] == "":
                    self.selectedMove = (self.selectedMove+1)%4

        elif self.instance == "paused":
            if button in self.controls["start"]:
                self.instance = "map"
                if self.debug:
                    print("INSTANCE:",self.instance)

        elif self.instance == "interaction":
            if button in self.controls["TRIANGLE"]:
                self.currentSentence += 1
                if self.currentSentence == len(self.speechList[0]):
                    self.instance = "map"

        elif self.instance == "baracks":
            if button in self.controls["left"]:
                if len(self.baracksOption) == 2:
                    self.baracksOption[1] = (self.baracksOption[1]-1)%len(self.party)

                elif self.baracksOption[0] == "Abilities": 
                    if len(self.baracksOption) == 3:
                        self.baracksOption[2] -= 10
                        if self.baracksOption[2] < 0:
                            print(self.baracksOption[2], self.movesListLength%10)
                            if abs(self.baracksOption[2]) <= 10-self.movesListLength%10:
                                self.baracksOption[2] += 10
                            else:
                                self.baracksOption[2] += 20
                    
                    elif len(self.baracksOption) == 4:
                        if self.abilityNavigation == [2,2]:
                            self.baracksOption[3] -= -1 + 2*(self.baracksOption[3]%2)
                                
            if button in self.controls["right"]:
                if len(self.baracksOption) == 2:
                    self.baracksOption[1] = (self.baracksOption[1]+1)%len(self.party)

                elif self.baracksOption[0] == "Abilities":                    
                    if len(self.baracksOption) == 3:
                        self.baracksOption[2] += 10
                        if self.baracksOption[2] >= self.movesListLength:
                            self.baracksOption[2] %= 10

                    elif len(self.baracksOption) == 4:
                        if self.abilityNavigation == [2,2]:
                            self.baracksOption[3] += 1 - 2*(self.baracksOption[3]%2)
                
            if button in self.controls["up"]:
                if len(self.baracksOption) == 1:
                    self.baracksOption = [self.baracksGraph[self.baracksOption[0]]["up"]]

                elif self.baracksOption[0] == "Abilities":
                    if len(self.baracksOption) == 3:
                        self.baracksOption[2] -= 1
                        self.baracksOption[2] %= self.movesListLength
                        print(self.movesListLength)

                    elif len(self.baracksOption) == 4:
                        if self.abilityNavigation == [2,2]:
                            self.baracksOption[3] -= 2
                            self.baracksOption[3] %= 4
                    
                if self.debug:
                    print(self.baracksOption)
            
            if button in self.controls["down"]:
                if len(self.baracksOption) == 1:
                    self.baracksOption = [self.baracksGraph[self.baracksOption[0]]["down"]]

                elif self.baracksOption[0] == "Abilities":
                    if len(self.baracksOption) == 3:
                        self.baracksOption[2] += 1
                        self.baracksOption[2] %= self.movesListLength
                        print(self.movesListLength)

                    elif len(self.baracksOption) == 4:
                        if self.abilityNavigation == [2,2]:
                            self.baracksOption[3] += 2
                            self.baracksOption[3] %= 4
                        
                if self.debug:
                    print(self.baracksOption)

            if button in self.controls["CROSS"]:
                if self.baracksOption[0] != "":
                    self.baracksOption.append(0)
                    if self.baracksOption[0] == "Abilities":
                        if len(self.baracksOption) == 5:
                            move = self.party[self.baracksOption[1]].getLearnedMoves()[self.baracksOption[2]][0]
                            self.party[self.baracksOption[1]].commands[self.baracksOption[3]+self.changeAbility] = move
                            if self.debug:
                                print(self.party[0].commands,self.party[1].commands)
                            self.party[self.baracksOption[1]].updateCommands()
                            self.baracksOption.pop()
                            self.baracksOption.pop()
                            
                if self.debug:
                    print(self.baracksOption)

            if button in self.controls["CIRCLE"]:
                self.baracksOption.pop()
                if len(self.baracksOption) == 0:
                    self.instance = "map"
                    self.baracksAnimation = [0,0,0]
                    self.baracksOption = [""]
                    if self.debug:
                        print("INSTANCE:",self.instance)
                        
                elif len(self.baracksOption) == 3:
                    self.baracksAnimation = [0,0,0.15]
                print(self.baracksOption)
                
            if button in self.controls["start"]:
                self.instance = "map"
                self.baracksAnimation = [0,0,0]
                self.baracksOption = [""]
                if self.debug:
                    print("INSTANCE:",self.instance)
               
    def update(self):
        startTime = pygame.time.get_ticks() #Get time so that the game runs for 60ps
        self.returnToMenu = False
        self.interactSelected = False
        #Get inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

            #Game Pad test
            if event.type == pygame.JOYBUTTONDOWN:
                self.handleInput(event.button)

            if event.type == pygame.KEYDOWN:
                self.handleInput(event.key)
                
            if self.gamePad != None:
                dpad = self.gamePad.get_hat(0)
                if self.instance == "baracks":
                    if dpad[1] == 1:
                        if len(self.baracksOption) == 1:
                            self.baracksOption = [self.baracksGraph[self.baracksOption[0]]["up"]]
                            
                    if dpad[1] == -1:
                        if len(self.baracksOption) == 1:
                            self.baracksOption = [self.baracksGraph[self.baracksOption[0]]["down"]]
                            
        if not self.returnToMenu:
            if self.instance == "map":
                if self.player != "":
                    if self.player.animations[0] == "": #If there are no animations playing
                        #Game Pad test
                        if self.gamePad != None:
                            x = self.gamePad.get_axis(0)
                            y = self.gamePad.get_axis(1)
                            if abs(x) > 0.01 and abs(y) > 0.01: #Pygame won't make it equal 0 at the center but instead a very small number
                                self.player.setAngle(x, y)
                                modulus = math.sqrt(x**2 + y**2)
                                if modulus > 0.65:
                                    self.player.moveForward()
                        
                        keys = pygame.key.get_pressed()

                        if keys[self.controls["up"][0]]:
                            self.player.moveForward()

                        if keys[self.controls["left"][0]]:
                            self.player.rotate(-1)

                        if keys[self.controls["right"][0]]:
                            self.player.rotate(1)

            #Call object clock cycles and capture data
            cameraData = []
            i = 0
            #coordinates, name
            nearest_location = [-1, ""]
            nearest_interaction = [-1, ""]
            if self.instance == "map":
                self.interactTip = ""
            #Command data
            commandData = []
            while i < len(self.entities): 
                #Bullet collision checker script
                if self.instance == "map":
                    if not(self.entities[i].tag in self.immortalEntities):
                        j = 0
                        while j < len(self.projectiles):
                            if self.entities[i].tag in self.entityGroups[self.projectiles[j].target] and self.entities[i].health > 0: #If entity is in the bullet's target group and alive
                                x,y = self.projectiles[j].x,self.projectiles[j].y
                                distance = math.sqrt((y-self.entities[i].y)**2+(x-self.entities[i].x)**2)
                                #Will check if bullet is in the entity's sphere
                                if distance <= self.entities[i].size:
                                    bullet = ((x,y),self.projectiles[j].size,self.projectiles[j].attack)
                                    hasBeenHit = self.entities[i].collision(bullet[0],bullet[1],bullet[2])
                                    if hasBeenHit != None:
                                        if hasBeenHit[1] and (self.entities[i].tag in self.entityGroups["enemy"]): #Award the player exp killing an enemy
                                            exp = (self.entities[i].level)*20 + 30
                                            if self.debug:
                                                print("EXP:",self.player.exp,"+"+str(exp))
                                            levelUp = self.player.checkLevel(exp)
                                            if levelUp:
                                                print("level up")
                                        instruction = self.projectiles[j].hasHit()
                                        if instruction != None:
                                            commandData.append(instruction)
                                        self.projectiles.pop(j)
                                        
                            j += 1 #Increment the loop
                            
                update = self.entities[i].update(((self.player.x,self.player.y),self.player.size),self.instance)
                if update != 0: #0 = signal to delete the object
                    if not(type(update) is tuple): #Convert update to a list/tuple
                        update = (update,) #0 makes it an ar
                    if update[0] == "location":
                        update = update[1] #Remove meta data
                        #check for nearby locations
                        if nearest_location[0] == -1:
                            nearest_location = update
                        elif nearest_location[0] > update[0]:
                            nearest_location = update
                    elif update[0] == "npc":
                        update = update[1] #Remove meta data
                        #check for nearby npcs
                        if nearest_interaction[0] == -1:
                            nearest_interaction = update
                            if self.instance == "map":
                                self.interactTip = nearest_interaction[7]
                        elif nearest_interaction[0] > update[0]:
                            nearest_interaction = update
                    elif update[0] == "bullet": #An entity wants to fire a bullet
                        self.runCommand(update[0], update[1])

                    #Pass alive enemies to the camera who are not the focus
                    if self.entities[i] != self.focus:
                        cameraData.append((self.entities[i].tag,self.entities[i].renderData(),self.entities[i].size,(self.entities[i].health,self.entities[i].maxHp)))
                    i += 1
                else:
                    #Remove dead enemies
                    self.entities.pop(i)
                    
            #Add projectiles to camera data
            i = 0
            while i < len(self.projectiles):
                update = self.projectiles[i].update(((self.player.x,self.player.y),),self.instance)
                #0 = signal to delete the object
                if update != 0:
                    cameraData.append((self.projectiles[i].tag,self.projectiles[i].renderData(),self.projectiles[i].size))
                    i += 1
                else:
                    self.projectiles.pop(i)

            #Add animations to the camera data
            i = 0
            playerAnimation = self.player.animations[0]
            while i < len(self.animations):
                if self.animations[i].tag in self.playerAnimations:
                    update = self.animations[i].update({"isRunning":playerAnimation,"position":(self.player.x,self.player.y)},self.instance)
                if update != 0:
                    cameraData.append((self.animations[i].tag,self.animations[i].renderData(),self.animations[i].size))
                    i +=1
                else:
                    self.animations.pop(i)

            #Execute the command data
            for i in range (len(commandData)):
                self.runCommand(commandData[i][0],commandData[i][1])
     
            #Check if the user wants to interact with something
            if self.interactSelected:
                if not(self.instance in self.pausedInstances):
                    if nearest_interaction[0] != -1:
                        if self.interactTip == "Converse":
                            self.instance = "interaction"
                            self.speechList = [nearest_interaction[5], nearest_interaction[1], nearest_interaction[2], nearest_interaction[6]] #Store the interaction data
                            #Text, name, colour is the order
                            self.currentSentence = 0
                        elif self.interactTip == "Station Baracks":
                            self.instance = "baracks"
                            if self.debug:
                                print("INSTANCE:",self.instance)
                            self.interactTip = ""
                        elif self.interactTip == "World Hub":
                            self.toggleSocket()
                            
            #Add any multiplayer players
            for i in range(len(self.multiplayerEntities)):
                cameraData.append((self.multiplayerEntities[i].tag,self.multiplayerEntities[i].renderData(),self.multiplayerEntities[i].size,(self.multiplayerEntities[i].health,self.multiplayerEntities[i].maxHp)))

            #Add location name to camera data
            cameraData.append(nearest_location)
            cameraData.append(nearest_interaction)
            if self.networkSocket != None: #Send data to all players
                j = 0
                while j < len(self.connectedAddresses):
                    try:
                        focusData = self.focus.tag,self.focus.renderData(),self.focus.size,(self.focus.health,self.focus.maxHp)
                        self.networkSocket.sendto(json.dumps(focusData).encode(), self.connectedAddresses[j])
                        for k in range(len(cameraData)-2): #-2 removes the nearest location and npc
                            self.networkSocket.sendto(json.dumps(cameraData[k]).encode(), self.connectedAddresses[j])
                        self.networkSocket.sendto(json.dumps(["1"]).encode(), self.connectedAddresses[j])
                        j += 1
                    except:
                        print("connection dropped: SEND ERROR")
                        self.connectedAddresses.pop(j)
                        self.activeAddresses.pop(j)
                        self.multiplayerEntities.pop(j)
                        print(self.connectedAddresses, self.multiplayerEntities)

            #Pass data to camera
            miniMapData = self.camera.render(cameraData)
            #Pass hud data to hud
            hudData = ((self.player.health,self.player.maxHp),(self.player.mana,self.player.maxMp),self.interactTip)
            self.hud.update(self.player.commandOptions, self.player.getCooldowns(), self.selectedMove, miniMapData, hudData)
                            
            if self.instance in self.pausedInstances: #Dim the screen
                dimEffect = pygame.Surface(self.dimensions, pygame.SRCALPHA)
                if self.instance == "baracks":
                    dimEffect.fill((100, 33, 114,140))
                else:
                    dimEffect.fill((0,0,0,140))
                self.surface.blit(dimEffect,(0,0))
                if self.instance == "baracks":
                    dimLine = pygame.Surface((self.dimensions[0],4), pygame.SRCALPHA)
                    dimLine.fill((0,0,0,100))
                    for i in range(round((self.dimensions[1]*0.7)//4 - 1)):
                        self.surface.blit(dimLine,(0,self.dimensions[1]*0.15+(i+1)*8))
                if self.instance == "paused":
                    text = self.menuFont.render("Paused", True, (249,179,27))
                    location = text.get_rect()
                    location.center = (self.dimensions[0]/2, self.dimensions[1]/2)
                    self.surface.blit(text, location)

                #Display the speech
                elif self.instance == "interaction":
                    pygame.draw.rect(self.surface, (0,0,0), self.speechBox)#Black backgroud
                    pygame.draw.rect(self.surface, self.speechList[3], self.speechBox, 4)#Box's border

                    for i in range(len(self.speechList[0][self.currentSentence])):
                        speech = self.speechList[0][self.currentSentence][i]
                        text = self.npcFont.render(speech, True, self.speechList[3])
                        location = text.get_rect()
                        location.topleft = (self.speechBox[0]+20, self.dimensions[1]-180+i*(location[3]+2))
                        self.surface.blit(text, location)
                    
                    name = self.npcNameFont.render(self.speechList[1], True, self.speechList[3])
                    nameSpace = name.get_rect()
                    nameBox = pygame.Rect(0,0, nameSpace[2]+80, nameSpace[3]+10)
                    nameBox.bottomleft = self.speechBox.topleft
                    pygame.draw.rect(self.surface, (0,0,0), nameBox)#Name background
                    pygame.draw.rect(self.surface, self.speechList[3], nameBox, 4)#Background's border
                    nameSpace.center = nameBox.center
                    self.surface.blit(name, nameSpace)

                elif self.instance == "baracks":
                    yDrop = self.baracksAnimation[0]
                    xShift = self.baracksAnimation[1]
                    headerDrop = self.baracksAnimation[2]
                    title = self.menuFont.render("Station Baracks",True,(89,88,183))#Title
                    titleRect = title.get_rect()
                    titleRect.bottomleft = (self.dimensions[0]*0.1, self.dimensions[1]*headerDrop/2)
                    pygame.draw.rect(self.surface, (11,14,32), (0, 0, self.dimensions[0], self.dimensions[1]*headerDrop)) #Header
                    pygame.draw.line(self.surface, (89,88,183), (0, self.dimensions[1]*headerDrop+2.5), (self.dimensions[0],self.dimensions[1]*headerDrop+2.5), 5) #Header border
                    pygame.draw.rect(self.surface, (11,14,32), (0, self.dimensions[1]*(1-headerDrop), self.dimensions[0], self.dimensions[1]*0.15)) #Footer
                    pygame.draw.line(self.surface, (89,88,183), (0, self.dimensions[1]*(1-headerDrop)-2.5), (self.dimensions[0],self.dimensions[1]*(1-headerDrop)-2.5), 5) #Footer border 
                    self.surface.blit(title,titleRect)

                    if len(self.baracksOption) < 3:
                        footerText = self.npcFont.render("Customise and view your party.", True, (109,142,224))
                        fTextRect = footerText.get_rect()
                        fTextRect.bottomleft = (self.dimensions[0]*0.1, self.dimensions[1]*(1-headerDrop)+self.dimensions[1]*0.08)
                        self.surface.blit(footerText, fTextRect)

                    if self.baracksOption[0] == "Abilities":
                        if len(self.baracksOption) > 2:
                            playerName = self.party[self.baracksOption[1]].displayName
                            playerNameRect = playerName.get_rect()
                            playerNameRect.topleft = (self.dimensions[0]*0.05, self.dimensions[1]*headerDrop/2 + 10)
                            self.surface.blit(playerName,playerNameRect)
                            pygame.draw.rect(self.surface, (22,27,63), (self.dimensions[0]*(0.05-xShift),self.dimensions[1]*0.15+5,self.dimensions[0]*0.65,self.dimensions[1]*0.7-10)) #Moves box
                            pygame.draw.rect(self.surface, self.infoBoxColour, (self.dimensions[0]*(0.75+yDrop*2),self.dimensions[1]*0.15+5,self.dimensions[0]*0.2,self.dimensions[1]*0.7-10)) #Moves information
                            movesList = self.party[self.baracksOption[1]].getLearnedMoves()
                            currentMove = 0
                            self.movesListLength = len(movesList)
                            for i in range(max(1, len(movesList)//4)):
                                for j in range(min(10, self.movesListLength-i*10)):
                                    abilityRect = pygame.Rect(0,0,self.dimensions[0]*0.15,self.dimensions[1]*0.05)
                                    abilityRect.topleft = (self.dimensions[0]*(0.05-xShift)+self.dimensions[0]*0.01+self.dimensions[0]*0.16*i,  self.dimensions[1]*0.168+self.dimensions[1]*0.068*j)
                                    colour = (120,120,120)
                                    if currentMove == self.baracksOption[2]: #If selected
                                        colour = (240,240,240)
                                        selected = (abilityRect, movesList[currentMove][0])
                                        self.infoBoxColour = [(movesList[currentMove][1][0])[0],(movesList[currentMove][1][0])[1],(movesList[currentMove][1][0])[2]]
                                        for k in range(len(self.infoBoxColour)): self.infoBoxColour[k] = max(0,self.infoBoxColour[k]-15) #Darken colour
                                        pygame.draw.rect(self.surface, (173,6,6), (abilityRect[0]-3,abilityRect[1]-3,abilityRect[2]+6,abilityRect[3]+6))

                                        for k in range(len(movesList[currentMove][1][1])): #Description
                                            text = movesList[currentMove][1][1][k]
                                            footerText = self.npcNameFont.render(text, True, (109,142,224))
                                            fTextRect = footerText.get_rect()
                                            fTextRect.bottomleft = (self.dimensions[0]*0.1, self.dimensions[1]*0.93+k*(fTextRect[3]+2))
                                            self.surface.blit(footerText, fTextRect)
                                            
                                    text = self.npcNameFont.render(movesList[currentMove][0], True, colour) #240,240,240
                                    textRect = text.get_rect()
                                    textRect.center = abilityRect.center
                                    pygame.draw.rect(self.surface, movesList[currentMove][1][0], abilityRect)
                                    self.surface.blit(text, textRect)
                                    currentMove += 1
                                        
                            #Draw the hand for the selected option
                            fingerRect = pygame.Rect(0,0,self.dimensions[0]*0.035,self.dimensions[1]*0.015)
                            palmRect = pygame.Rect(0,0,self.dimensions[0]*0.025, self.dimensions[1]*0.025)
                            fingerRect.midright = selected[0].midleft
                            palmRect.topleft = fingerRect.bottomleft
                            pygame.draw.rect(self.surface, (240,240,240), palmRect)
                            pygame.draw.rect(self.surface, (30,30,30), palmRect, 2)
                            pygame.draw.rect(self.surface, (240,240,240), fingerRect)
                            pygame.draw.rect(self.surface, (30,30,30), fingerRect, 2)

                            #Draw the stats for the selected option
                            stats = self.player.getDictionary()[selected[1]] #Player stores the dictionary
                            keys = ("Attack %: ","Power %: ", "Mana Cost: ", "Cooldown: ")
                            for i in range(1, 5):
                                info = stats[i]
                                if i < 3:
                                    info = round(info*100)
                                text = self.npcNameFont.render(keys[i-1]+str(info), True, (240,240,240))
                                location = text.get_rect()
                                location.center = (self.dimensions[0]*(0.85+yDrop*2), self.dimensions[1]*0.1+self.dimensions[1]*0.15*i)
                                self.surface.blit(text, location)

                            if len(self.baracksOption) == 4: #Draw the change commands option
                                boxColour = self.infoBoxColour[0] #Store its red value
                                if boxColour == 94 or boxColour == 0: #Attack command
                                    rect = pygame.Rect(0,0,self.dimensions[0]*0.12, self.dimensions[1]*0.06)
                                    currentCommand = pygame.Rect(0,0,self.dimensions[0]*0.1, self.dimensions[1]*0.04)
                                    rect.topleft = selected[0].topright
                                    currentCommand.center = rect.center
                                    if boxColour == 94:
                                        text = self.party[self.baracksOption[1]].commands[0]
                                        self.changeAbility = 0
                                    else:
                                        text = self.party[self.baracksOption[1]].commands[5]
                                        self.changeAbility = 5
                                    colour = [self.infoBoxColour[0]*2,self.infoBoxColour[1]*2,self.infoBoxColour[2]*2] #Passes data by value
                                    pygame.draw.rect(self.surface, (160,160,160), rect)
                                    pygame.draw.rect(self.surface, colour, currentCommand)
                                    text = self.npcNameFont.render(text, True, (240,240,240))
                                    textRect = text.get_rect()
                                    textRect.center = currentCommand.center
                                    self.surface.blit(text, textRect)
                                    handRect = currentCommand
                                    self.abilityNavigation = [1,0]
                                    
                                elif boxColour == 10:
                                    rect = pygame.Rect(0,0,self.dimensions[0]*0.24, self.dimensions[1]*0.12)
                                    miniRects = (pygame.Rect(0,0,self.dimensions[0]*0.12, self.dimensions[1]*0.06),
                                                 pygame.Rect(0,0,self.dimensions[0]*0.12, self.dimensions[1]*0.06),
                                                 pygame.Rect(0,0,self.dimensions[0]*0.12, self.dimensions[1]*0.06),
                                                 pygame.Rect(0,0,self.dimensions[0]*0.12, self.dimensions[1]*0.06)
                                                 )
                                    currentCommands = (pygame.Rect(0,0,self.dimensions[0]*0.1, self.dimensions[1]*0.04),
                                                       pygame.Rect(0,0,self.dimensions[0]*0.1, self.dimensions[1]*0.04),
                                                       pygame.Rect(0,0,self.dimensions[0]*0.1, self.dimensions[1]*0.04),
                                                       pygame.Rect(0,0,self.dimensions[0]*0.1, self.dimensions[1]*0.04)
                                                )
                                    commands = self.party[self.baracksOption[1]].commands
                                    texts = []
                                    rect.topleft = selected[0].topright
                                    miniRects[0].topleft = rect.topleft
                                    miniRects[1].topleft = miniRects[0].topright
                                    miniRects[2].topleft = miniRects[0].bottomleft
                                    miniRects[3].topleft = miniRects[2].topright
                                    for i in range(4):
                                        currentCommands[i].center = miniRects[i].center
                                        texts.append([self.npcNameFont.render(commands[i+1], True, (240,240,240))])
                                        texts[i].append(texts[i][0].get_rect())
                                        texts[i][1].center = currentCommands[i].center
                                        if self.baracksOption[3] == i:
                                            handRect = texts[i][1]
                                    colour = [self.infoBoxColour[0]*2,self.infoBoxColour[1]*2,self.infoBoxColour[2]*2] #Passes data by value
                                    pygame.draw.rect(self.surface, (160,160,160), rect)
                                    for commandRect in currentCommands:
                                        pygame.draw.rect(self.surface, colour, commandRect)
                                    for text in texts:
                                        self.surface.blit(text[0],text[1])
                                    self.abilityNavigation = [2,2]
                                    self.changeAbility = 1
                                
                                #Draw the hand for the selected slot
                                fingerRect = pygame.Rect(0,0,self.dimensions[0]*0.023,self.dimensions[1]*0.010)
                                palmRect = pygame.Rect(0,0,self.dimensions[0]*0.016, self.dimensions[1]*0.016)
                                fingerRect.midright = handRect.midleft
                                palmRect.topleft = fingerRect.bottomleft
                                pygame.draw.rect(self.surface, (240,240,240), palmRect)
                                pygame.draw.rect(self.surface, (30,30,30), palmRect, 2)
                                pygame.draw.rect(self.surface, (240,240,240), fingerRect)
                                pygame.draw.rect(self.surface, (30,30,30), fingerRect, 2)
                                
                    if xShift > 0:
                        colours = []
                        optionsText = ["Items","Equipment","Abilities","Customise","Status","Config"]
                        for i in range(6):
                            optionsBox = pygame.Rect(self.dimensions[0]*0.1, self.dimensions[1]*((yDrop+0.05)+i*0.08), self.dimensions[0]*0.15, self.dimensions[1]*(min(yDrop,0.06)))
                            colours.append(((10,5,25),(120,120,120)))
                            if self.baracksOption[0] == optionsText[i]:
                                colours[i] = (56,9,5),(240,240,240)
                                pygame.draw.rect(self.surface, (168,24,11), (optionsBox[0]-4,optionsBox[1]-4,optionsBox[2]+8,optionsBox[3]+8))
                            optionsText[i] = self.npcFont.render(optionsText[i],True,colours[i][1])
                            textLocation = optionsText[i].get_rect()
                            textLocation.center = optionsBox.center
                            pygame.draw.rect(self.surface, colours[i][0], optionsBox)
                            self.surface.blit(optionsText[i], textLocation)

                        pygame.draw.rect(self.surface, (89,88,183), (self.dimensions[0]*(1-xShift), self.dimensions[1]*0.25, self.dimensions[0]*0.6, self.dimensions[1]*0.5)) #Ally portrait box
                        pygame.draw.rect(self.surface, (44,54,126), (self.dimensions[0]*(1-xShift), self.dimensions[1]*0.25, self.dimensions[0]*0.6, self.dimensions[1]*0.5), 4) #Ally portrait Frame
                        
                        pygame.draw.rect(self.surface, (22,27,63), (self.dimensions[0]*(1-xShift), self.dimensions[1]*0.6, self.dimensions[0]*0.6, self.dimensions[1]*0.075)) #Ally information name
                        pygame.draw.rect(self.surface, (0,0,0), (self.dimensions[0]*(1-xShift), self.dimensions[1]*0.675, self.dimensions[0]*0.6, self.dimensions[1]*0.15)) #Ally information stats
                        pygame.draw.rect(self.surface, (44,54,126), (self.dimensions[0]*(1-xShift), self.dimensions[1]*0.6, self.dimensions[0]*0.6, self.dimensions[1]*0.225), 4) #Ally information Frame
                        pygame.draw.rect(self.surface, (44,54,126), (self.dimensions[0]*(1-xShift), self.dimensions[1]*0.6, self.dimensions[0]*0.6, self.dimensions[1]*0.075), 4) #Part of the frame
                        labelText = [
                            self.npcNameFont.render("LV",True,(232,203,74)),
                            self.npcNameFont.render("HP",True,(87,114,51)),
                            self.npcNameFont.render("MP",True,(59,102,135))
                        ]
                        labelRects = [text.get_rect() for text in labelText]
                        for i in range(3):
                            labelRects[i].midleft = (self.dimensions[0]*(1-xShift)+15, self.dimensions[1]*(0.675+0.0375) +i*self.dimensions[1]*0.0375)
                            self.surface.blit(labelText[i], labelRects[i])
                        pygame.draw.line(self.surface, (44,54,126), (self.dimensions[0]*(1.05-xShift),self.dimensions[1]*0.6), (self.dimensions[0]*(1.05-xShift),self.dimensions[1]*0.825), 4) #Stats
                        for i in range(4):
                            repeatedCalculation = self.dimensions[0]*0.1375
                            x = self.dimensions[0]*(1.05-xShift)+(i+1)*repeatedCalculation
                            pygame.draw.line(self.surface, (44,54,126), (x,self.dimensions[1]*0.6), (x,self.dimensions[1]*0.825), 4) #Dividers
                            if i < len(self.party):
                                rectX = self.dimensions[0]*(1.05-xShift)+(i)*repeatedCalculation
                                nameRects = pygame.Rect(rectX,self.dimensions[1]*0.6,repeatedCalculation,self.dimensions[1]*0.075)
                                info = self.party[i].getInfo()
                                level = info["level"]
                                health = info["health"]
                                mana = info["mana"]
                                memberImage = self.party[i].getImage(repeatedCalculation/2, "display")
                                imageCenter = (nameRects[0] + nameRects[2]/2, self.dimensions[1]*0.425)
                                for point in memberImage:
                                    point[0] += imageCenter[0]
                                    point[1] += imageCenter[1]
                                pygame.draw.aalines(self.surface, self.party[i].baseColour, True, memberImage)
                                playerName = self.party[i].displayName
                                playerNameRect = playerName.get_rect()
                                playerNameRect.center = nameRects.center
                                if len(self.baracksOption) == 2:
                                    if self.baracksOption[1] == i:
                                        self.surface.blit(self.transRedSurface, nameRects.topleft)
                                self.surface.blit(playerName, playerNameRect)
                                informationText = [
                                    self.npcNameFont.render(level,True,(232,203,74)),
                                    self.npcNameFont.render(health,True,(87,114,51)),
                                    self.npcNameFont.render(mana,True,(59,102,135)),
                                ]
                                for j in range(3):
                                    informationRect = informationText[j].get_rect()
                                    informationRect.midright = (x-10,labelRects[j].midright[1])
                                    self.surface.blit(informationText[j], informationRect)

                    if len(self.baracksOption) == 1:             
                        if self.baracksAnimation[0] < 0.15:
                            self.baracksAnimation[0] += 0.03
                            self.baracksAnimation[1] += 0.14

                    elif len(self.baracksOption) == 2:             
                        if self.baracksAnimation[0] < 0.15:
                            self.baracksAnimation[0] += 0.03
                            self.baracksAnimation[1] += 0.14
                            
                    elif len(self.baracksOption) == 3:
                        if self.baracksAnimation[0] > 0:
                            self.baracksAnimation[0] -= 0.06
                            self.baracksAnimation[1] -= 0.28
                            if self.baracksAnimation[0] < 0:
                                self.baracksAnimation[0] = 0
                                self.baracksAnimation[1] = 0
                            
                    if self.baracksAnimation[2] < 0.15:
                            self.baracksAnimation[2] += 0.03
            
            pygame.display.update()
            
            #Check for inactive addresses
            i = 0
            while i < (len(self.activeAddresses)):
                self.activeAddresses[i] += 16
                if self.activeAddresses[i] > 200:
                    print("connection dropped: INACTIVE")
                    self.connectedAddresses.pop(i)
                    self.activeAddresses.pop(i)
                    self.multiplayerEntities.pop(i)
                else:
                    i += 1
                    
            deltaTime = pygame.time.get_ticks()-startTime #Get time so that the game runs for 60ps
            pygame.time.delay(max(16-deltaTime,0))
            
        else:
            return 0

    def toggleSocket(self):
        if self.debug:
            if self.networkSocket == None:
                self.networkSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.networkSocket.bind((self.SERVER_IP,self.SERVER_PORT))
                if self.debug:
                    print("SERVER OPENED")
                _thread.start_new_thread(self.udp_thread, ())

            else:
                self.networkSocket.close()
                self.networkSocket = None
                self.multiplayerEntities = []
                self.activeAddresses = []
                self.connectedAddresses = []
                if self.debug:
                    print("SERVER CLOSED")

    def udp_thread(self):
        while True:
            try:
                data, address = self.networkSocket.recvfrom(4096)
                if not(address in self.connectedAddresses):
                    print(address)
                    self.connectedAddresses.append(address)
                    self.activeAddresses.append(0)
                    self.multiplayerEntities.append(objects.player(str(address), self.player.stats, (0,0,0), 30))
                data = data.decode()
                for i in range(len(self.multiplayerEntities)): #Find the correct player
                    if self.multiplayerEntities[i].tag == str(address):
                        slot = i
                        self.activeAddresses[slot] = 0
                data = json.loads(data)
                self.multiplayerEntities[slot].x = data[0]
                self.multiplayerEntities[slot].y = data[1]
                self.multiplayerEntities[slot].angle = data[2]
            except Exception as e:
                if self.networkSocket == None:
                    break
                else:
                    pass
            
class camera:
    def __init__(self, surface, dimensions, debug):
        self.debug = debug
        self.surface = surface
        self.width = dimensions[0]
        self.length = dimensions[1]
        self.entityHealthBars = ("triangle","square")
        self.healthBarLength = 30
        self.healthBarHeight = 18
        self.boundary = [self.width/2, self.length/2]
        self.focus = None
        if self.debug == True:
            self.colour = (0,0,0)
        else:
            self.colour = (0,0,0)
        self.path = getRootFolder(2)
        self.locationFont = pygame.font.Font(setPath(self.path,["assets","fonts","Kingdom_Hearts_Font.ttf"]), 50)
        self.npcFont = pygame.font.Font(setPath(self.path,["assets","fonts","Coda-Regular.ttf"]), 30)
        self.font = pygame.font.Font(pygame.font.get_default_font(), 10)

    def distance(self, point1, point2):
        x1 = point1[0]
        y1 = point1[1]
        x2 = point2[0]
        y2 = point2[1]
        return x2-x1, y2-y1

    def setFocus(self, focus):
        self.focus = focus

    def render(self, data):
        if self.debug == True:
            self.surface.fill((255,255,255))
        else:
            self.surface.fill((255,255,255))
        miniMapData = []
        #Set the camera's constants
        focusData = self.focus.renderData("camera") #Mode 1 = center mode
        focusX,focusY = focusData[0]
        focusImage = focusData[1]
        focusColour = focusData[2]
        camShiftX = self.width/2 - focusX
        camShiftY = self.length/2 - focusY
        #See if monsters are close enough to be rendered
        #data format:
        "i = monster"
        "[i][0] = tag"
        "[i][1][0] = coordinates"
        "[i][1][1] = points to draw"
        "[i][1][2] = colour"
        "[i][2] = size"
        "[i][3][0] = health"
        "[i][3][1] = max health"
        for i in range(len(data)-2):
            distance = self.distance(data[i][1][0], (focusX,focusY))
            colour = data[i][1][2]
            if abs(distance[0]) <= self.boundary[0]+data[i][2] and abs(distance[1]) <= self.boundary[1]+data[i][2]:
                for j in range(len(data[i][1][1])):
                    data[i][1][1][j][0] += camShiftX #Shift entity to the screen
                    data[i][1][1][j][1] += camShiftY #Shift entity to the screen
                entity = data[i][1][1] #Store points to draw
                if self.debug == True: #Render coordinates
                    x = round(data[i][1][0][0])
                    y = round(data[i][1][0][1])
                    position = self.font.render(str((x,y)), True, self.colour)
                    location = position.get_rect()
                    location.center = (data[i][1][0][0]+camShiftX, data[i][1][0][1]+camShiftY)
                    self.surface.blit(position, location)
                pygame.draw.aalines(self.surface, colour, True, entity) #Render entity
                if data[i][0] in self.entityHealthBars: #Render health bar
                    x = data[i][1][0][0] +camShiftX -self.healthBarLength/2 -data[i][2]/2 
                    y = data[i][1][0][1]-data[i][2]-self.healthBarHeight+camShiftY
                    healthPercentage = data[i][3][0]/data[i][3][1]
                    pygame.draw.rect(self.surface, (150,30,30), (x, y ,self.healthBarLength+data[i][2], data[i][2]/4))#Hp Bar Background
                    pygame.draw.rect(self.surface, (30,150,30), (x+(self.healthBarLength+data[i][2])*(1-healthPercentage), y, (self.healthBarLength+data[i][2])*healthPercentage+0.5, data[i][2]/4))#Hp Bar
                    pygame.draw.rect(self.surface, (130,30,30), (x, y ,self.healthBarLength+data[i][2], data[i][2]/4), 2)#Hp Bar Frae
            #Get minimap data
            "tag, (minimapX, minimapY), size, colour"
            if data[i][0] != "location":
                if abs(distance[0]) <= 1500 and abs(distance[1]) <= 1500:
                    #Tag, position, size
                    miniMapData.append((data[i][0],(distance[0], distance[1]), data[i][2], colour))
            else:
                #Allows location area to be radius
                if abs(distance[0]) <= 1500+data[i][2]*10 and abs(distance[1]) <= 1500+data[i][2]*5:
                    #Tag, position, size
                    miniMapData.append((data[i][0],(distance[0], distance[1]), data[i][2], colour))
        #Render focus at the center
        for i in range(len(focusImage)):
            focusImage[i][0] += self.width/2
            focusImage[i][1] += self.length/2
        if self.debug == True:
            x,y = round(focusX),round(focusY)
            position = self.font.render(str((x,y)), True, self.colour)
            location = position.get_rect()
            location.center = (self.width/2, self.length/2)
            self.surface.blit(position, location)
        pygame.draw.aalines(self.surface, focusColour, True, focusImage)
        #Render the nearest location
        end = len(data)-2
        text = data[end][1]
        if text != "":
            text = self.locationFont.render(text, True, data[end][2])
            location = text.get_rect()
            location.topright = (self.width-30, 179)
            self.surface.blit(text, location)
        #Render the nearest npc
        end = len(data)-1
        text = data[end][1]
        if text != "":
            text = self.npcFont.render(text, True, data[end][2])
            location = text.get_rect()
            x = data[end][3][0] + camShiftX
            y = data[end][3][1] + camShiftY + data[end][4] + 20
            location.center = (x, y)
            self.surface.blit(text, location)
        return miniMapData

        
