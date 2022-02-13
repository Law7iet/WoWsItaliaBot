# https://www.mongodb.com/languages/python

import pymongo
from utils import *
from bson import ObjectId

class ApiMongoDB:
    def __init__(self):
        self.project = "WoWsItaliaBot"
        self.databaseName = "WoWsItaliaBotDB"
        self.configCollectionName = "Config"
        self.clanCollectionName = "Clans"

        self.client = pymongo.MongoClient("mongodb+srv://" + config.data["MONGO_USER"] + ":" + config.data["MONGO_PASSWORD"] + "@cluster0.rtvit.mongodb.net/" + self.project + "?retryWrites=true&w=majority")

    # Parametric API to mongo
    def __getElement(self, collection, query):
        try:
            if collection == Collection.CONFIG:
                return self.client[self.databaseName][self.configCollectionName].find_one(query)
            elif collection == Collection.CLANS:
                return self.client[self.databaseName][self.clanCollectionName].find_one(query)
            else:
                return None
        except:
            return None

    def __getElements(self, collection, query):
        try:
            if collection == Collection.CONFIG:
                return self.client[self.databaseName]["Config"].find(query)
            elif collection == Collection.CLANS:
                return self.client[self.databaseName]["Clans"].find(query)
            else:
                return None
        except:
            return None

    def __insertElement(self, collection, element):
        try:
            if collection == Collection.CONFIG:
                return self.client[self.databaseName]["Config"].insert_one(element)
            elif collection == Collection.CLANS:
                return self.client[self.databaseName]["Clans"].insert_one(element)
            else:
                return None
        except:
            return None

    def __updateElement(self, collection, filter, element):
        try:
            if collection == Collection.CONFIG:
                return self.client[self.databaseName]["Config"].update_one(filter, element)
            elif collection == Collection.CLANS:
                return self.client[self.databaseName]["Clans"].update_one(filter, element)
            else:
                return None
        except:
            return None

    def __deleteElement(self, collection, query):
        try:
            if collection == Collection.CONFIG:
                return self.client[self.databaseName]["Config"].delete_one(query)
            elif collection == Collection.CLANS:
                return self.client[self.databaseName]["Clans"].delete_one(query)
            else:
                return None
        except:
            return None

    # API to Config file
    def getConfig(self):
        return self.__getElement(Collection.CONFIG, {})
    
    def updateConfig(self, configData):
        return self.__updateElement(Collection.CONFIG, {"_id": ObjectId(getConfigId())}, {"$set": configData})

    # API to Clans Colletion
    def getClanById(self, clanId):
        return self.__getElement(Collection.CLANS, {"id": str(clanId)})

    def getClansByTag(self, clanTag):
        return list(self.__getElements(Collection.CLANS, {"tag": {"$regex": clanTag, "$options": "i"}}))

    def getClansByName(self, clanName):
        return list(self.__getElements(Collection.CLANS, {"name": {"$regex": clanName, "$options": "i"}}))

    def insertClan(self, clanInfo):
        if self.getClanById(str(clanInfo["id"])) != None:
            return None
        r1 = None
        r2 = None
        try:
            r1 = str(clanInfo["representations"][0])
            r2 = str(clanInfo["representations"][1])
        except:
            pass
        return self.__insertElement(
            Collection.CLANS,
            {
                "id": str(clanInfo["id"]),
                "name": str(clanInfo["name"]),
                "tag": str(clanInfo["tag"]),
                "representations": [
                    r1,
                    r2
                ]
            })

    def updateClan(self, clanId, clanData):
        return self.__updateElement(Collection.CLANS, {"id": clanId}, clanData)

    def deleteClan(self, clanId):
        return self.__deleteElement(Collection.CLANS, {"id": clanId})