import math
from src import filePath

#Loads contents and mods
#Order of priority
#0 base game files
#1-10 Mods
#Any clashes will result in the lower numbered file overwritting the other file
#Clashes between files of the same priority will favour the latter file
#e.g. two mods add in an enemy with the same name, only the enemy from the mod
#with the higher priority will be added in.

#Constants
FILERETRACTS = 2

fileRootPath = filePath.getRootFolder(FILERETRACTS)

#Load enemy data
def loadEnemyData():
    contentFolder = filePath.setPath(fileRootPath ,["data","content","enemies.txt"])
    contentData = filePath.loadConfig(contentFolder)
    return contentData

def load_projectile_data():
    content_folder = filePath.setPath(fileRootPath ,["data", "content", "projectiles.txt"])
    content_data = filePath.loadConfig(content_folder)
    for key in content_data:
        mapping = content_data[key][1]
        for polar_coordinate in mapping:
            polar_coordinate[1] *= math.pi / 180
    return content_data

def loadEntities():
    entities = [loadEnemyData(), load_projectile_data()]
    return entities

def loadAbilities():
    contentFolder = filePath.setPath(fileRootPath, ["data", "content", "abilities.txt"])
    contentData = filePath.loadList(contentFolder)
    return contentData
