class cursor:
    
    def __init__(self):
        self.x = -1
        self.y = 0
        pass

    def setTrack(self, layout):
        self.layout = layout

    def moveRight(self):
        if self.x == -1:
            self.x, self.y = 0, 0
        else:
            self.x += 1
            if self.x > len(self.layout[self.y])-1:
                self.x = 0
                self.y += 1
            if self.y > len(self.layout)-1:
                self.y = 0
            while self.layout[self.y][self.x] == ' ':
                self.moveRight()

    def moveLeft(self):
        if self.x == -1:
            self.x, self.y = 0, 0
        else:
            self.x -= 1
            if self.x < 0:
                self.y = (self.y-1)%len(self.layout)
                self.x = len(self.layout[self.y])-1
            while self.layout[self.y][self.x] == ' ':
                self.moveLeft()

    def moveUp(self):
        if self.x == -1:
            self.x, self.y = 0, 0
        else:
            self.y = (self.y-1)%len(self.layout)
            while self.layout[self.y][self.x] == ' ':
                self.moveRight()

    def moveDown(self):
        if self.x == -1:
            self.x, self.y = 0, 0
        else:
            self.y = (self.y-1)%len(self.layout)
            while self.layout[self.y][self.x] == ' ':
                self.moveLeft()
                
    def setCursor(self, x, y):
        self.x = x
        self.y = y
        
    def getCursor(self):
        return self.x, self.y, self.layout[self.y][self.x]
