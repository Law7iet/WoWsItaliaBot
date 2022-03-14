# Documentation: https://www.mongodb.com/languages/python

from bson import ObjectId
from pymongo import MongoClient, cursor, results
from utils.constants import *
from utils.functions import getConfigId
import config


class ApiMongoDB:
    def __init__(self):
        self.project = "WoWsItaliaBot"
        self.database_name = "WoWsItaliaBotDB"
        self.config_collection_name = "Config"
        self.clan_collection_name = "Clans"

        self.client = MongoClient("mongodb+srv://" + config.data["MONGO_USER"] + ":" + config.data["MONGO_PASSWORD"] + "@cluster0.rtvit.mongodb.net/" + self.project + "?retryWrites=true&w=majority")

    # Parametric API to mongo
    def __get_element(self, collection: DatabaseCollection, query: dict) -> any | None:
        """
        Get an element which match with the query from a collection of the database.
        If an error occurs, it returns `None`.

        Args:
            collection (`DatabaseCollection`): _description_
            query (`dict`): _description_

        Returns:
            `any` | `None`: _description_
        """        
        try:
            if collection == DatabaseCollection.CONFIG:
                return self.client[self.database_name][self.config_collection_name].find_one(query)
            elif collection == DatabaseCollection.CLANS:
                return self.client[self.database_name][self.clan_collection_name].find_one(query)
            else:
                return None
        except:
            return None

    def __get_elements(self, collection: DatabaseCollection, query: dict) -> cursor.Cursor | None:
        """_summary_

        Args:
            collection (DatabaseCollection): _description_
            query (dict): _description_

        Returns:
            cursor.Cursor | None: _description_
        """        
        try:
            if collection == DatabaseCollection.CONFIG:
                return self.client[self.database_name]["Config"].find(query)
            elif collection == DatabaseCollection.CLANS:
                return self.client[self.database_name]["Clans"].find(query)
            else:
                return None
        except:
            return None

    def __insert_element(self, collection: DatabaseCollection, element: dict) -> results.InsertOneResult | None:
        """_summary_

        Args:
            collection (DatabaseCollection): _description_
            element (dict): _description_

        Returns:
            results.InsertOneResult | None: _description_
        """        
        try:
            if collection == DatabaseCollection.CONFIG:
                return self.client[self.database_name]["Config"].insert_one(element)
            elif collection == DatabaseCollection.CLANS:
                return self.client[self.database_name]["Clans"].insert_one(element)
            else:
                return None
        except:
            return None

    def __update_element(self, collection: DatabaseCollection, filter: dict, element: dict) -> results.UpdateResult | None:
        """_summary_

        Args:
            collection (DatabaseCollection): _description_
            filter (dict): _description_
            element (dict): _description_

        Returns:
            results.UpdateResult | None: _description_
        """        
        try:
            if collection == DatabaseCollection.CONFIG:
                return self.client[self.database_name]["Config"].update_one(filter, element)
            elif collection == DatabaseCollection.CLANS:
                return self.client[self.database_name]["Clans"].update_one(filter, element)
            else:
                return None
        except:
            return None

    def __delete_element(self, collection: DatabaseCollection, query: dict) -> results.DeleteResult | None:
        """_summary_

        Args:
            collection (DatabaseCollection): _description_
            query (dict): _description_

        Returns:
            results.DeleteResult | None: _description_
        """                
        try:
            if collection == DatabaseCollection.CONFIG:
                return self.client[self.database_name]["Config"].delete_one(query)
            elif collection == DatabaseCollection.CLANS:
                return self.client[self.database_name]["Clans"].delete_one(query)
            else:
                return None
        except:
            return None

    # API to Config file
    def get_config(self) -> any | None:
        """_summary_

        Returns:
            any | None: _description_
        """        
        return self.__get_element(DatabaseCollection.CONFIG, {})
    
    def update_config(self, config_data: dict) -> results.UpdateResult | None:
        """_summary_

        Args:
            config_data (dict): _description_

        Returns:
            results.UpdateResult | None: _description_
        """        
        return self.__update_element(DatabaseCollection.CONFIG, {"_id": ObjectId(getConfigId())}, {"$set": config_data})

    # API to Clans Colletion
    def get_clan_by_id(self, clan_id: str) -> any | None:
        """_summary_

        Args:
            clan_id (str): _description_

        Returns:
            any | None: _description_
        """        
        return self.__get_element(DatabaseCollection.CLANS, {"id": clan_id})

    def get_clans_by_tag(self, clan_tag: str) -> list | None:
        """_summary_

        Args:
            clan_tag (str): _description_

        Returns:
            list | None: _description_
        """        
        x = self.__get_elements(DatabaseCollection.CLANS, {"tag": {"$regex": clan_tag, "$options": "i"}})
        if x:
            return list(x)
        else:
            return None

    def get_clans_by_name(self, clan_name: str) -> list | None:
        """_summary_

        Args:
            clan_name (str): _description_

        Returns:
            list | None: _description_
        """        
        x = self.__get_elements(DatabaseCollection.CLANS, {"name": {"$regex": clan_name, "$options": "i"}})
        if x:
            return list(x)
        else:
            return None

    def insert_clan(self, clan_info: dict) -> results.InsertOneResult | None:
        """_summary_

        Args:
            clan_info (dict): _description_

        Returns:
            results.InsertOneResult | None: _description_
        """        
        if self.get_clan_by_id(str(clan_info["id"])) != None:
            return None
        r1 = None
        r2 = None
        try:
            r1 = str(clan_info["representations"][0])
            r2 = str(clan_info["representations"][1])
        except:
            pass
        return self.__insert_element(
            DatabaseCollection.CLANS,
            {
                "id": str(clan_info["id"]),
                "name": str(clan_info["name"]),
                "tag": str(clan_info["tag"]),
                "representations": [
                    r1,
                    r2
                ]
            })

    def update_clan(self, clan_id: str, clan_data: dict) -> results.UpdateResult | None:
        """_summary_

        Args:
            clan_id (str): _description_
            clan_data (dict): _description_

        Returns:
            results.UpdateResult | None: _description_
        """        
        return self.__update_element(DatabaseCollection.CLANS, {"id": clan_id}, clan_data)

    def delete_clan(self, clan_id: str) -> results.DeleteResult | None:
        """_summary_

        Args:
            clan_id (str): _description_

        Returns:
            results.DeleteResult | None: _description_
        """        
        return self.__delete_element(DatabaseCollection.CLANS, {"id": clan_id})