import pygame
import math, random
import json

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

def loadConfig(filePath):
    try:
        config = open(filePath).readlines()
        config = [x.strip() for x in config]
        dicte = "{"
        for i in range(len(config)):
            if config[i][0] != "#": #Ignore comments
                dicte += config[i]+','
        dicte = dicte[:-1]
        dicte += "}"
        config = json.loads(dicte)
        return config
    except:
        return 0 #loading error
    
def distanceLinePoint(line, point, size, test=""):
    x0 = point[0]
    y0 = point[1]
    x1 = line[0][0]
    y1 = line[0][1]
    x2 = line[1][0]
    y2 = line[1][1]
    #Check if point is within rectangle surrounding bordering the line
    if x0 >= min(x1,x2) and x0 <= max(x1,x2) and y0 >= min(y1,y2) and y0 <= max(y1,y2):
        distance = abs((y2-y1)*x0-(x2-x1)*y0+x2*y1-y2*x1)/math.sqrt((y2-y1)**2+(x2-x1)**2)
        return distance <= 4+size #The constant, 4, is the leiniency of the hitbox

def pointToPoint(xDif, yDif, angle):
    if yDif < 0:
        return  math.pi/2 - math.atan(xDif/yDif) 
    else:
        if yDif != 0:
            return - math.pi/2 - math.atan(xDif/yDif)
        else:
            return angle #returned when angle can not be calculated

        #(-1*yDif/abs(yDif)) = math.atan(xDif/yDif) One line equation

class entity:
    def __init__(self, tag, stats, position=(0,0,0), size=30, dimensions=(1280,720)):
        self.tag = tag
        self.stats = stats
        self.x = position[0]
        self.y = position[1]
        self.angle = position[2]
        self.visualAngle = self.angle
        self.displayAngle = 0
        self.size = size
        self.dimensions = dimensions
        self.speed = 3
        self.clock = 0
        self.animations = [""]
        self.iFrame = False #immunity frame
        self.dodgeFrame = False #ignore collision frame
        self.passives = []
        #Collision complexity
        self.complexity = 10
        #Conditions (e.g. hp, mana, cooldowns, is alive?)
        self.loadConditions()
        
    def loadConditions(self):
        try:
            self.name = self.stats["name"]
        except:
            self.name = self.tag+":nameNotSet"
        if self.tag == "player":
            space = self.dimensions[0]*0.1375
            fSize = 30
            path = getRootFolder(2)
            fittedFont = pygame.font.Font(setPath(path,["assets","fonts","Coda-Regular.ttf"]), fSize)
            self.displayName = fittedFont.render(self.name,True,(200,200,200))
            spaceTaken = self.displayName.get_rect()[2]
            while spaceTaken > space-10:
                fSize -= 1
                fittedFont = pygame.font.Font(setPath(path,["assets","fonts","Coda-Regular.ttf"]), fSize)
                self.displayName = fittedFont.render(self.name,True,(200,200,200))
                spaceTaken = self.displayName.get_rect()[2]
        try:
            self.health = self.stats["hp"]
        except:
            self.health = 10
        try:
            self.mana = self.stats["mp"]
        except:
            self.mana = 2
        try:
            self.maxHp = self.stats["maxHp"]
        except:
            self.maxHp = self.health
        try:
            self.colour = self.stats["colour"]
        except:
            self.colour = (0,0,0)
        self.baseColour = self.colour
        try:
            self.speed = self.stats["speed"]
        except:
            pass
        try:
            self.attack = self.stats["attack"]
        except:
            self.attack = 2
        try:
            self.level = self.stats["level"]
        except:
            self.level = 1

    def moveForward(self, distance=None):
        if distance == None:
            self.x += self.speed*math.cos(self.angle)
            self.y += self.speed*math.sin(self.angle)
        else:
            self.x += distance*math.cos(self.angle)
            self.y += distance*math.sin(self.angle)

    def rotate(self, strength):
        if strength == 1:
            self.angle += self.speed/80
        elif strength == -1:
            self.angle -= self.speed/80        
        else:
            self.angle += strength
        self.angle %= 2*math.pi

    def setAngle(self, cxAxis, cyAxis): #cxAxis = controller X Axis
        self.angle = pointToPoint(-1*cxAxis, -1*cyAxis, self.angle) #-1 inverts it so that it works for pygame

    def getImage(self, size, mode=0):
        x,y = self.x,self.y
        if mode == "camera":
            x,y = 0,0
        if mode == "display":
            x,y = 0,0
            display = self.visualAngle
            self.visualAngle = self.displayAngle
            self.displayAngle += 0.05
        point1 = [x+size*math.cos(self.visualAngle), y+size*math.sin(self.visualAngle)]
        point2 = [x+size*math.cos(self.visualAngle+math.pi/2), y+size*math.sin(self.visualAngle+math.pi/2)]
        point3 = [x+size*math.cos(self.visualAngle+math.pi), y+size*math.sin(self.visualAngle+math.pi)]
        point4 = [x+size*math.cos(self.visualAngle+(3*math.pi/2)), y+size*math.sin(self.visualAngle+(3*math.pi/2))]
        if mode == "display":
            self.visualAngle = display
        return point1,point2,point3,point4

    def collision(self, bullet, bulletSize, damage):
        if self.tag == "location" or self.tag == "npc" or self.dodgeFrame:
            pass
        else:
            return self.bulletCollision(bullet, bulletSize, damage)
    
    def bulletCollision(self, bullet, bulletSize, damage):
        dead = False
        currentSize = self.size
        linesToCheck = []
        for i in range(self.complexity): #Load boundaries
            currentSize -= self.size/self.complexity
            boundaries = self.getImage(currentSize, 0) 
            for j in range(len(boundaries)): linesToCheck.append(boundaries[j]) #Add each line individually to the list
        for i in range(len(linesToCheck)): #Check collisions with the boundaries
            isCollided = distanceLinePoint((linesToCheck[i],linesToCheck[(i+1)%len(linesToCheck)]), bullet, bulletSize, self.tag)
            if isCollided:
                dead = False
                self.hitProcedure(damage)
                if self.health <= 0:
                    dead = True
                return True,dead

    def renderData(self, mode=0):
        return (self.x,self.y),self.getImage(self.size,mode),self.colour

    def hitProcedure(self, damage):
        if self.iFrame == False:
            self.health -= damage
        elif self.animations[0] == "guard":
            if self.animations[1] > -300: #Stops permanent stun
                self.animations[1] -= 100 #Extend the duration
            if "burly vampire" in self.passives: #Activate a passive
                self.health += self.maxHp*0.04
                if self.health > self.maxHp:
                    self.health = self.maxHp
        
    def update(self, externalData=[], instance="map"):
        if instance == "map":
            self.visualAngle += math.pi/800
            self.visualAngle %= 2*math.pi  

            self.clock += 16
            self.clock %= 960

class location(entity):
    def __init__(self, tag, stats, position=(0,0,0), size=60, dimensions=(1280,720)):
        super().__init__(tag, stats, position, size, dimensions)
        self.speed = 1

    def getImage(self, size, mode=0):
        x,y = self.x,self.y
        if mode == "camera":
            x,y = 0,0
        point1 = [x+size*math.cos(self.visualAngle), y+size*math.sin(self.visualAngle)]
        point2 = [x+size*math.cos(self.visualAngle+math.pi/2), y+size*math.sin(self.visualAngle+math.pi/2)]
        point3 = [x+size*math.cos(self.visualAngle+math.pi), y+size*math.sin(self.visualAngle+math.pi)]
        point4 = [x+size*math.cos(self.visualAngle+(3*math.pi/2)), y+size*math.sin(self.visualAngle+(3*math.pi/2))]
        return point1,point2,point3,point4

    def update(self, externalData=[], instance="map"):
        if instance == "map":
            #AI
            self.visualAngle += math.pi/800
            self.visualAngle %= 2*math.pi  

            self.clock += 16
            self.clock %= 960
            
        returns = []
        if externalData != []:
            playerx, playery = externalData[0]
            distance = math.sqrt((self.y-playery)**2 + (self.x-playerx)**2)
            if distance <= self.size*5:
                returns = ("location",(distance, self.name, self.colour))
                
        if returns != []:
            return returns

class triangle(entity):
    def __init__(self, tag, stats, position=(0,0,0), size=30, dimensions=(1280,720)):
        super().__init__(tag, stats, position, size, dimensions)
        if self.name.lower() == "purple bandit": #Custom mosnter
            self.speed = 3
            self.size = 70
            self.attack = 8
            self.level = 5
            self.ai = {"range":300,"followRange":600,"fireRate":[1200,1200],"bulletType":"surge","bulletSize":13,"bulletSpeed":11}
        else:
            self.speed = 4
            self.attack = 3
            self.ai = {"range":250,"followRange":400,"fireRate":[1200,1200],"bulletType":"surge","bulletSize":9,"bulletSpeed":9}
            
        self.fireRate = self.ai["fireRate"]
        self.shots = 0

    def getImage(self, size, mode=0):
        x,y = self.x,self.y
        if mode == "camera":
            x,y = 0,0
        if mode == "display":
            x,y = 0,0
            display = self.angle
            self.angle = self.displayAngle
            self.displayAngle += 0.05
        point1 = [x+size*math.cos(self.angle), y+size*math.sin(self.angle)]
        point2 = [x+size*math.cos(self.angle+(7*math.pi)/9), y+size*math.sin(self.angle+(7*math.pi)/9)]
        point3 = [x+size*math.cos(self.angle-(7*math.pi)/9), y+size*math.sin(self.angle-(7*math.pi)/9)]
        if mode == "display":
            self.angle = display
        return point1,point2,point3
    
    def update(self, externalData=[], instance="map"):
        if instance == "map":
            returns = []
            if self.health > 0:
                #AI
                playerx,playery = externalData[0]
                playerSize = externalData[1]
                distance = math.sqrt((self.y-playery)**2 + (self.x-playerx)**2)
                        
                if distance <= self.ai["followRange"]: #Move towards player if they are within the follow range
                    self.angle = pointToPoint((self.x-playerx),(self.y-playery), self.angle)
                    if distance > self.ai["range"]: #Check how close the player is
                        self.moveForward()
                    
                    if self.fireRate[0] >= self.fireRate[1]:
                        self.fireRate[0] = 0
                        if self.shots != 2:
                            returns = ("bullet",((self.ai["bulletType"].lower(), {"critical":False,"attack":self.attack,"speed":self.ai["bulletSpeed"],"target":"ally","colour":(220,50,50)}, [self.x,self.y,self.angle], self.ai["bulletSize"]),))
                        else:
                            returns = ("bullet",(("shotgun", {"critical":False,"attack":self.attack*0.7,"speed":self.ai["bulletSpeed"],"target":"ally","colour":self.colour}, [self.x,self.y,self.angle], self.ai["bulletSize"]+3),))
                            self.shots = -1
                        self.shots += 1
                        
                else: #Move randomly if too far
                    if self.clock < 960:
                        self.moveForward()
                        self.rotate(-1)
                    elif self.clock < 1920:
                        self.rotate(1)
                        self.rotate(1)
                    elif self.clock < 2880:
                        self.moveForward()
                        self.rotate(1)
                    
                self.clock += 16
                self.clock %= 2880

                if self.fireRate[0] < self.fireRate[1]:
                    self.fireRate[0] += 16
                                   
                if returns != []:
                    return returns
            else:
                return 0

class square(entity):
    def __init__(self, tag, stats, position=(0,0,0), size=30, dimensions=(1280,720)):
        super().__init__(tag, stats, position, size, dimensions)
        self.speed = 2
        self.visualAngle = self.angle

    def getImage(self, size, mode=0):
        x,y = self.x,self.y
        if mode == "camera":
            x,y = 0,0
        if mode == "display":
            x,y = 0,0
            display = self.visualAngle
            self.visualAngle = self.displayAngle
            self.displayAngle += 0.05
        point1 = [x+size*math.cos(self.visualAngle), y+size*math.sin(self.visualAngle)]
        point2 = [x+size*math.cos(self.visualAngle+math.pi/2), y+size*math.sin(self.visualAngle+math.pi/2)]
        point3 = [x+size*math.cos(self.visualAngle+math.pi), y+size*math.sin(self.visualAngle+math.pi)]
        point4 = [x+size*math.cos(self.visualAngle+(3*math.pi/2)), y+size*math.sin(self.visualAngle+(3*math.pi/2))]
        if mode == "display":
            self.visualAngle = display
        return point1,point2,point3,point4

    def update(self, externalData=[], instance="map"):
        if instance == "map":
            if self.health > 0:
                #AI
                if self.clock < 960:
                    self.moveForward()
                    self.moveForward()
                elif self.clock < 1920:
                    self.rotate(math.pi/60)
                elif self.clock < 2880:
                    self.moveForward()
                    self.moveForward()
                    self.moveForward()
                    self.moveForward()
                elif self.clock < 3840:
                    self.rotate(math.pi/60)
                elif self.clock < 4800:
                    self.moveForward()
                    self.moveForward()
                self.visualAngle += math.pi/50
                self.visualAngle %= 2*math.pi

                self.clock += 16
                self.clock %= 4800
            else:
                return 0
                                                       
class player(entity):
    def __init__(self, tag, stats, position=(0,0,0), size=30, dimensions=(1280,720)):
        super().__init__(tag, stats, position, size, dimensions)
        self.speed = 6
        self.items = []
        self.animationColours = ((50,50,200),)
        self.animationList = ("Guard","Dodge","Super Dodge","Light Dash")
        self.savedData = self.stats["savedData"]
        self.items = self.savedData[5]
        self.commands = self.savedData[7]["commands"]
        self.calculateAttributes(self.savedData[1],self.savedData[3],self.savedData[4])
        self.passives = ["burly vampire"]
        self.commandOptions = ("Attack","Magic","Items","Drive")
        self.lastSelected = None
        self.difficulty = self.savedData[0]
        
        try:
            self.name = self.savedData[7]["name"]
        except:
            self.name == "Player Nathan"
        space = self.dimensions[0]*0.1375
        fSize = 30
        path = getRootFolder(2)
        fittedFont = pygame.font.Font(setPath(path,["assets","fonts","Coda-Regular.ttf"]), fSize)
        self.displayName = fittedFont.render(self.name,True,(200,200,200))
        spaceTaken = self.displayName.get_rect()[2]
        while spaceTaken > space-10:
            fSize -= 1
            fittedFont = pygame.font.Font(setPath(path,["assets","fonts","Coda-Regular.ttf"]), fSize)
            self.displayName = fittedFont.render(self.name,True,(200,200,200))
            spaceTaken = self.displayName.get_rect()[2]
            
        self.health = self.maxHp
        self.mana = self.maxMp

    def getImage(self, size, mode=0): #mode 0 = center, mode 0 = 1 position for colission
        x,y = self.x,self.y
        if mode == "camera":
            x,y = 0,0
        if mode == "display":
            x,y = 0,0
            display = self.angle
            self.angle = self.displayAngle
            self.displayAngle += 0.01
        point1 = [x+size*math.cos(self.angle), y+size*math.sin(self.angle)]
        point2 = [x+size*math.cos(self.angle+(7*math.pi)/9), y+size*math.sin(self.angle+(7*math.pi)/9)]
        point3 = [x+size*math.cos(self.angle-(7*math.pi)/9), y+size*math.sin(self.angle-(7*math.pi)/9)]
        if mode == 0 and (self.animations[0] == "guard" or self.animations[0] == "light dash"):
            size += 10
            point1 = [x+size*math.cos(self.angle), y+size*math.sin(self.angle)]
            point2 = [x+size*math.cos(self.angle+math.pi/2), y+size*math.sin(self.angle+math.pi/2)]
            point3 = [x+size*math.cos(self.angle+math.pi), y+size*math.sin(self.angle+math.pi)]
            point4 = [x+size*math.cos(self.angle+(3*math.pi/2)), y+size*math.sin(self.angle+(3*math.pi/2))] 
            return point1,point2,point3,point4
        if mode == "display":
            self.angle = display
        return point1,point2,point3

    def activateCommand(self, commandSlot):
        option = None
        if commandSlot < 4:
            option = self.commandOptions[commandSlot]
            
        if option == "Attack": #Attack
            return self.runCommand(0)
        
        elif option == "Magic":
            self.commandOptions = (self.commands[1],self.commands[2],self.commands[3],self.commands[4])
            self.lastSelected = 1

        elif option == "Items":
            self.commandOptions = ("","","","")
            self.lastSelected = 2

        elif option == "Drive":
            self.commandOptions = ("","","","")
            self.lastSelected = 3

        else:
            return self.runCommand(commandSlot+1)
                
    def runCommand(self, commandSlot): #Currently disabled to test new version
        if self.animations[0] == "": #If there are no animations playing
            currentCommand = self.commandsData[commandSlot]
            manaCost = currentCommand["cost"]
            if (manaCost == 0 or self.mana > 0) and self.coolDowns[commandSlot][0] >= self.coolDowns[commandSlot][1]:
                isCritical = random.randint(1,100)
                if isCritical <= round(self.critRate):
                    isCritical = True
                else:
                    isCritical = False
                self.coolDowns[commandSlot][0] = 0
                self.mana -= manaCost
                if self.mana < 0 and manaCost != 0:
                    self.mana = 0
                self.health += self.maxHp*currentCommand["heal"]
                if self.health > self.maxHp:
                    self.health = self.maxHp
                commandName = self.commands[commandSlot].lower()
                if currentCommand["type"] == "bullet":
                    if isCritical:
                        if commandSlot == 0:
                            return ("bullet",
                                    (
                                        (commandName,
                                           {"critical":False,"target":"enemy","colour":self.colour,"attack":currentCommand["attack"],"speed":currentCommand["speed"]},
                                           [self.x,self.y,self.angle],
                                           currentCommand["size"]
                                     ),
                                        (commandName,
                                           {"critical":True,"target":"enemy","colour":self.colour,"attack":currentCommand["attack"],"speed":currentCommand["speed"]},
                                           [self.x,self.y,self.angle],
                                           currentCommand["size"]
                                     ),
                                    )
                                )
                        else:
                            if commandName == "combo":
                                commandName = self.commands[0].lower()
                                currentCommand = self.commandsData[0]
                                return ("bullet",
                                    (
                                        (commandName,
                                           {"critical":False,"target":"enemy","colour":self.colour,"attack":currentCommand["attack"],"speed":currentCommand["speed"]},
                                           [self.x,self.y,self.angle],
                                           currentCommand["size"]
                                     ),
                                        (commandName,
                                           {"critical":True,"target":"enemy","colour":self.colour,"attack":currentCommand["attack"],"speed":currentCommand["speed"]},
                                           [self.x,self.y,self.angle],
                                           currentCommand["size"]
                                     ),
                                        (commandName,
                                           {"critical":False,"target":"enemy","colour":self.colour,"attack":currentCommand["attack"],"speed":currentCommand["speed"]*0.6},
                                           [self.x,self.y,self.angle],
                                           currentCommand["size"]
                                     ),
                                        (commandName,
                                           {"critical":True,"target":"enemy","colour":self.colour,"attack":currentCommand["attack"],"speed":currentCommand["speed"]*0.6},
                                           [self.x,self.y,self.angle],
                                           currentCommand["size"]
                                     ),  
                                    )
                                )
                            return ("bullet", ((commandName,
                                       {"critical":True,"target":"enemy","colour":self.colour,"attack":currentCommand["attack"],"speed":currentCommand["speed"]},
                                       [self.x,self.y,self.angle],
                                       currentCommand["size"]),)
                            )
                    else:
                        if commandName == "combo":
                            commandName = self.commands[0].lower()
                            currentCommand = self.commandsData[0]
                            return ("bullet",
                                    (
                                        (commandName,
                                           {"critical":False,"target":"enemy","colour":self.colour,"attack":currentCommand["attack"],"speed":currentCommand["speed"]},
                                           [self.x,self.y,self.angle],
                                           currentCommand["size"]
                                     ),
                                        (commandName,
                                           {"critical":False,"target":"enemy","colour":self.colour,"attack":currentCommand["attack"],"speed":currentCommand["speed"]*0.6},
                                           [self.x,self.y,self.angle],
                                           currentCommand["size"]
                                     ),
                                    )
                                )
                        return ("bullet", ((commandName,
                                           {"critical":False,"target":"enemy","colour":self.colour,"attack":currentCommand["attack"],"speed":currentCommand["speed"]},
                                           [self.x,self.y,self.angle],
                                           currentCommand["size"]),)
                                )
                if commandName == "teleport":
                    self.moveForward(250)

                elif commandName == "repair":
                    return("animation", (commandName,{"colour":(50,200,50),"speed":1,"duration":500},(self.x,self.y,self.angle), self.size+10))
                    
                elif currentCommand["type"] == "iframe":
                    self.iframe = True
                    self.animations = [commandName, 0]
                    if commandName == "guard" or commandName =="light dash":
                        return("animation", (commandName,{"colour":(50,50,200),"speed":5},(self.x,self.y,self.angle), self.size+15))
                        
    def updateCommands(self):
        self.commandsData = []
        while len(self.commands) < 6:
            self.commands.append("")
        for i in range(6):
            if self.commands[i] != "":
                data = commandDictionary[self.commands[i]]
                data = {"name":self.commands[i],"type":data[7], "heal":data[0], "attack":(self.attack*data[1]+self.power*data[2]), "cost":data[3], "cd":data[4]*1000*(1-self.coolDownReduction), "size":data[5], "speed":data[6]}
                if i == 0:
                    data["name"] = "Attack"
                self.commandsData.append(data)
            else:
                data = {"name":0,"type":0,"heal":0, "attack":0, "cost":0, "cd":0, "size":0, "speed":0}
                self.commandsData.append(data)
        self.coolDowns = [[data["cd"],data["cd"],data["name"]] for data in self.commandsData]
    
    #Generates stats from level, ship type and emblems, see ideas text file in the project's root folder.
    def calculateAttributes(self, exp, shipType, emblems):
        self.exp = exp
        if exp >= 300:
            self.level = math.floor(math.sqrt((exp-300)/70)-1)
            if self.level < 0:
                self.level = 0
        else:
            self.level = 0

        #Convert numbers to str
        ships = ("valour","wisdom","vanguard","recruit")

        if shipType == -1:
            self.shipType = "recruit"
        elif not(shipType in ships):
            self.shipType = ships[shipType]
            
        if emblems[0] == -1:
            self.emblems = "recruit"
        elif not(emblems[0] in ships):
            self.emblems = ships[emblems[0]]
            
        if emblems[1] == -1:
            self.emblems = (self.emblems,"recruit")
        elif not(emblems[1] in ships):
            self.emblems = (self.emblems,ships[emblems[1]])

        #Strength, Intelligence, Agility
        self.str,self.int,self.agi = 0,0,0

        #Stat growth changes based on ship type
        if self.shipType == "valour":
            self.str = self.level*3
        elif self.shipType == "wisdom":
            self.int = self.level*3
        elif self.shipType == "vanguard":
            self.agi = self.level*3

        #Stat growth based on emblems
        if self.emblems[0] == "valour":
            self.str += self.level*1
        elif self.emblems[0] == "wisdom":
            self.int += self.level*1
        elif self.emblems[0] == "vanguard":
            self.agi += self.level*1

        if self.emblems[1] == "valour":
            self.str += self.level//2
        elif self.emblems[1] == "wisdom":
            self.int += self.level//2
        elif self.emblems[1] == "vanguard":
            self.agi += self.level//2

        #Level bonuses stat boosts
        if self.level >= 2:
            self.int +=10
        if self.level >= 4:
            self.str += 10
            self.agi += 10
        if self.level >= 7:
            self.agi += 10
        if self.level >= 8:
            self.str += 20
        if self.level >= 11:
            self.str += 20
            self.agi += 20
        if self.level >= 15:
            self.int += 20

        #Reduced bonuses
        if self.level >= 20:
            self.str += 10
        if self.level >= 25:
            self.agi += 10
        if self.level >= 30:
           self.str += 10
        if self.level >= 35:
            self.int += 10
        if self.level >= 40:
            self.str += 10
        if self.level >= 45:
            self.agi += 10
        if self.level >= 50:
            self.str += 10
        if self.level >= 55:
            self.int += 20
        if self.level >= 60:
            self.str += 10
            self.int += 20
            self.agi += 20

        self.fetchLearnedMoves()
        self.calculateStats()
        self.updateCommands()

    def calculateStats(self):
        #Offensive stats
        self.attack = self.str*0.2 + self.agi*0.1 +4 #attack dmg
        self.power = self.int*0.3 + self.agi*0.1 +6 #ability dmg
        self.critRate = self.agi*0.2 #chance to deal 50% bonus ability damage or to fire an extra shot
        #Defensive stats
        self.maxHp = self.str*0.5 + self.int*0.1 + self.agi*0.1 +10
        self.maxMp = self.int*0.1 +1
        self.defence = self.str*0.1
        self.movementSpeed = 6*(1+self.agi*0.002) #6 is the base speed
        #Misc stats
        self.coolDownReduction = 0
        self.manaHaste = 0.45
        
    def fetchLearnedMoves(self):
        attackCommands = []
        path = getRootFolder(2) #2 retracts
        configPath = setPath(path,["data","configs","command_tree_attack.txt"])
        movesCanLearn = loadConfig(configPath)
        slot = ("valour","wisdom","engineer","recruit").index(self.shipType)
        for key in movesCanLearn.items():
            requiredLevel = movesCanLearn[key[0]][0][slot]
            if requiredLevel > -1 and self.level >= requiredLevel:
                attackCommands.append((key[0], ((109,31,23), movesCanLearn[key[0]][1])))
        attackCommands = sorted(attackCommands)

        abilityCommands = []
        path = getRootFolder(2) #2 retracts
        configPath = setPath(path,["data","configs","command_tree_ability.txt"])
        movesCanLearn = loadConfig(configPath)
        slot = ("valour","wisdom","engineer","recruit").index(self.shipType)
        for key in movesCanLearn.items():
            requiredLevel = movesCanLearn[key[0]][0][slot]
            if requiredLevel > -1 and self.level >= requiredLevel:
                abilityCommands.append((key[0], ((25,75,119), movesCanLearn[key[0]][1])))
        abilityCommands = sorted(abilityCommands)

        backCommands = []
        path = getRootFolder(2) #2 retracts
        configPath = setPath(path,["data","configs","command_tree_back.txt"])
        movesCanLearn = loadConfig(configPath)
        slot = ("valour","wisdom","engineer","recruit").index(self.shipType)
        for key in movesCanLearn.items():
            requiredLevel = movesCanLearn[key[0]][0][slot]
            if requiredLevel > -1 and self.level >= requiredLevel:
                backCommands.append((key[0], ((15,81,17), movesCanLearn[key[0]][1])))
        backCommands = sorted(backCommands)

        passiveCommands = []
        path = getRootFolder(2) #2 retracts
        configPath = setPath(path,["data","configs","command_tree_passive.txt"])
        movesCanLearn = loadConfig(configPath)
        slot = ("valour","wisdom","engineer","recruit").index(self.shipType)
        for key in movesCanLearn.items():
            requiredLevel = movesCanLearn[key[0]][0][slot]
            if requiredLevel > -1 and self.level >= requiredLevel:
                passiveCommands.append((key[0], ((80,80,80), movesCanLearn[key[0]][1])))
        passiveCommands = sorted(passiveCommands)

        self.learnedMoves = attackCommands+abilityCommands+backCommands+passiveCommands

    def getLearnedMoves(self):
        return self.learnedMoves

    def checkLevel(self, exp):
        if self.difficulty == 2:
            exp *= 0.8 #Decrease exp gain
        self.exp += exp
        print("EXP:",self.exp," +"+str(exp))
        level = self.level
        if self.exp >= 300:
            self.level = math.floor(math.sqrt((self.exp-300)/70)-1)
            if self.level < 0:
                self.level = 0
        else:
            self.level = 0
        if self.level > level:
            self.calculateAttributes(self.exp, self.shipType, self.emblems)
            self.health = self.maxHp
            self.mana = self.maxMp
            return True

    def setCommand(self, slot, command):
        self.commands[slot] = command

    #See load passives
    def getAttributes(self):
        return {"level":self.level,"shiptype":self.shipType,"emblems":self.emblems}

    def getStats(self):
        return {"attack":self.attack,"power":self.power,"critrate":self.critRate,"maxhp":self.maxHp,"maxmp":self.maxMp,"defence":self.defence,"speed":self.movementSpeed}

    def getInfo(self):
        mana = self.mana
        if mana < 0:
            mana = 0
        return {"level":str(self.level), "health":str(round(self.health))+"/  "+str(round(self.maxHp)), "mana":str(round(mana))+"/  "+str(round(self.maxMp))}
    
    def getCooldowns(self):
        return self.coolDowns

    def getDictionary(self):
        return commandDictionary
    
    def update(self, externalData=[], instance="map"):
        if instance == "map":
            if self.health > 0:
                for i in range (len(self.coolDowns)): #Cycle the cooldowns
                    if self.coolDowns[i][0] < self.coolDowns[i][1]:
                        if (self.commands[i] in self.animationList) and self.animations[0] == self.commands[i].lower():
                            pass #Don't cycle yet
                        else:
                            self.coolDowns[i][0] += 16
                if self.mana <= 0 and abs(self.mana) < self.maxMp: #Regenerate the mana
                    self.mana -= (self.maxMp/(30*(1-self.manaHaste)))/60 #30 = base duration in seconds
                elif abs(self.mana) >= self.maxMp:
                    self.mana = self.maxMp

                #Run any animations
                if self.animations[0] != "":
                    if self.animations[0] == "dodge":
                        self.dodgeFrame = True
                        self.moveForward(10)
                        self.colour = self.animationColours[0]
                        if self.animations[1] >= 200:
                            self.colour = self.baseColour
                            self.dodgeFrame = False
                            self.animations = ["",0]
                    elif self.animations[0] == "super dodge":
                        self.dodgeFrame = True
                        self.moveForward(12.5)
                        self.colour = self.animationColours[0]
                        if self.animations[1] >= 200:
                            self.colour = self.baseColour 
                            self.dodgeFrame = False
                            self.animations = ["",0]
                    elif self.animations[0] == "guard":
                        self.iFrame = True
                        self.colour = self.animationColours[0]
                        if self.animations[1] >= 300:
                            self.colour = self.baseColour
                            self.iFrame = False
                            self.animations = ["",0]
                    elif self.animations[0] == "light dash":
                        self.iFrame = True
                        self.colour = self.animationColours[0]
                        if self.animations[1] >= 300:
                            self.colour = self.baseColour
                            self.iFrame = False
                            self.animations = ["dodge",0]           
                            
                    self.animations[1] += 16 #Cycle animations
            else:
                self.x = 0
                self.y = 0
                self.health = self.maxHp

class npc(entity):
    def __init__(self, tag, stats, position=(0,0,0), size=30, dimensions=(1280,720)):
        super().__init__(tag, stats, position, size, dimensions)
        self.textColour = self.colour
        if self.textColour == (0,0,0): #If text is black make it lighter so that is readable
            self.textColour = (150,150,150)
        #Load text
        try:
            self.text = self.stats["speech"]
        except:
            self.text = ["Hello."]
        try:
            self.instance = self.stats["instance"]
        except:
            self.instance = ""
            
        if self.instance == "":
            self.interactionType = "Converse"
        else:
            self.interactionType = self.instance
            
    def update(self, externalData=[], instance="map"):
        if instance == "map":
            #AI
            self.visualAngle += math.pi/800
            self.visualAngle %= 2*math.pi  

            self.clock += 16
            self.clock %= 960

        returns = []
        if externalData != []:
            playerx, playery = externalData[0]
            distance = math.sqrt((self.y-playery)**2 + (self.x-playerx)**2)
            if distance <= self.size*3:
                returns = ("npc",(distance, self.name, self.colour, (self.x, self.y), self.size, self.text, self.textColour, self.interactionType))
                
        if returns != []:
            return returns
        
class bullet(entity):
    def __init__(self, tag, stats, position=(0,0,0), size=5):
        super().__init__(tag, stats, position, size)
        self.tag = self.tag.lower()
        self.target = self.stats["target"].lower()
        self.critical = self.stats["critical"]
        self.duration = 2000
        if self.tag == "arcanum":
            self.duration = 10000
            self.attack /= 8
            self.orbitRange = self.stats["range"]
        if self.critical:
            self.colour = (239,102,83)
            if self.tag == "surge" or self.tag == "shotgun" or self.tag == "hyper":
                self.size *= 0.8
                self.speed *= 1.2
            else:
                self.size *= 1.5
                self.attack *= 1.5

    def getImage(self, size, mode=0):
        if self.critical:
            point1 = [self.x+size*math.cos(self.visualAngle), self.y+size*math.sin(self.visualAngle)]
            point2 = [self.x+size*math.cos(self.visualAngle+math.pi/2), self.y+size*math.sin(self.visualAngle+math.pi/2)]
            point3 = [self.x+size*math.cos(self.visualAngle+math.pi), self.y+size*math.sin(self.visualAngle+math.pi)]
            point4 = [self.x+size*math.cos(self.visualAngle+(3*math.pi/2)), self.y+size*math.sin(self.visualAngle+(3*math.pi/2))]
            
            point5 = [self.x+size*math.cos(self.visualAngle), self.y+size*math.sin(self.visualAngle)]
            point6 = [self.x+size*math.cos(self.visualAngle+math.pi), self.y+size*math.sin(self.visualAngle+math.pi)]
            point7 = [self.x+size*math.cos(self.visualAngle+(3*math.pi/2)), self.y+size*math.sin(self.visualAngle+(3*math.pi/2))]
            point8 = [self.x+size*math.cos(self.visualAngle+math.pi/2), self.y+size*math.sin(self.visualAngle+math.pi/2)]
            return point1,point2,point3,point4,point5,point6,point7,point8 #point1,point3,point4,point2
        point1 = [self.x+size*math.cos(self.visualAngle), self.y+size*math.sin(self.visualAngle)]
        point2 = [self.x+size*math.cos(self.visualAngle+math.pi/2), self.y+size*math.sin(self.visualAngle+math.pi/2)]
        point3 = [self.x+size*math.cos(self.visualAngle+math.pi), self.y+size*math.sin(self.visualAngle+math.pi)]
        point4 = [self.x+size*math.cos(self.visualAngle+(3*math.pi/2)), self.y+size*math.sin(self.visualAngle+(3*math.pi/2))]
        return point1,point2,point3,point4

    def hasHit(self):
        #Any code to be run
        if self.tag == "missile":
            return ("bullet", (("explosion", 8, {"critical":self.critical,"target":self.target,"colour":self.colour,"attack":self.attack/10,"speed":4}, [self.x,self.y,self.angle], 12),))
    
    def update(self, externalData=[], instance="map"):
        if instance == "map":
            playerx,playery = externalData[0]
            if self.clock < self.duration:
                self.moveForward()
            else:
                return 0
            if self.tag == "arcanum":
                self.angle += math.pi/64
                self.x,self.y = playerx,playery
                self.moveForward(self.size+self.orbitRange)
            self.visualAngle += math.pi/20
            self.visualAngle %= 2*math.pi
            self.clock += 16
            if self.tag == "orbit": #Delete after 1 frame
                return 0

class animation(entity):
    def __init__(self, tag, stats, position=(0,0,0), size=5, dimensions=(1280,720)):
        super().__init__(tag, stats, position, size, dimensions)
        self.tag = self.tag.lower()
        self.spinAnimations = ("guard","barrier","light dash","repair","orbit")
        self.playerCurrentAnimations = ("guard","barrier","light dash")
        try:
            self.duration = [0,self.stats["duration"]]
        except:
            self.duration = None
        if self.tag == "orbit":
            self.size = 70
            self.speed = 1
            
    def getImage(self, size, mode=0):
        point1 = [self.x+size*math.cos(self.angle), self.y+size*math.sin(self.angle)]
        point2 = [self.x+size*math.cos(self.angle+math.pi/2), self.y+size*math.sin(self.angle+math.pi/2)]
        point3 = [self.x+size*math.cos(self.angle+math.pi), self.y+size*math.sin(self.angle+math.pi)]
        point4 = [self.x+size*math.cos(self.angle+(3*math.pi/2)), self.y+size*math.sin(self.angle+(3*math.pi/2))]
        return point1,point2,point3,point4
    
    def update(self, externalData=[], instance="map"):
        if instance == "map":
            if self.tag in self.spinAnimations:
                self.rotate(1)
                if self.speed < 15:
                    self.speed += 0.25
                    
            if externalData["isRunning"] != "":
                if self.tag == "light dash" and externalData["isRunning"] == "dodge":
                    return 0
            else:
                if self.tag in self.playerCurrentAnimations:
                    return 0
                
            if self.tag == "repair":
                self.x,self.y = externalData["position"]
                if self.duration[0] >= self.duration[1]:
                    return 0
                self.duration[0] += 16

            if self.tag == "orbit":
                self.size -= 0.5
                self.size = max(20, self.size)
                if self.clock >= 800:
                    return 0

            self.clock += 16
            self.clock %= 3200
            

#Test objects
if __name__ == "__main__":
    path = getRootFolder(2) #2 retracts
    configPath = setPath(path,["data","configs","commands.txt"])
    commandDictionary = loadConfig(configPath)
    
    '''#Valour Route Test
    dummy = player("player", {"colour":(0,50,0), "commands":["Surge","Aura","Shield","Repair"]}, (0,0,math.pi/2)) #Create dummy player
    dummy.calculateAttributes(15, "valour", ("",""))
    dummy.calculateStats()
    stats = dummy.getStats()
    keys = ["Attack: ","Power: ","Crit Rate: ","Max HP: ","Max MP: ","Defence: ","Movement Speed: "]
    for i in range(7):
        print(keys[i]+str(stats[i]))
    print(dummy.getAttributes())'''
else:
    path = getRootFolder(2) #2 retracts
    configPath = setPath(path,["data","configs","command_data.txt"])
    commandDictionary = loadConfig(configPath)
    

    
