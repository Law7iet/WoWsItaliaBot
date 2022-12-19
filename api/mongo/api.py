# Documentation: https://www.mongodb.com/languages/python

from bson import ObjectId
from pymongo import MongoClient, cursor, results

from models.my_enum.database_enum import DBCollections
from utils.functions import get_config_id


class ApiMongoDB:
    def __init__(self):
        self.database_name = "WoWsItaliaDB"
        self.client = MongoClient()

    ####################################################################################################################
    #                                                PRIVATE API                                                       #
    ####################################################################################################################
    # Parametric API to mongo
    def __get_element(self, collection: DBCollections, query: dict) -> any | None:
        """
        Gets an element which matches with `query` from a collection of the database.

        Args:
            collection: The collection of the database.
            query: The query.

        Returns:
            The result of the function `find_one`.
            If an error occurs, it returns `None`.
        """
        try:
            return self.client[self.database_name][str(collection)].find_one(query)
        except Exception as error:
            print(error)
            return None

    def __get_elements(self, collection: DBCollections, query: dict) -> cursor.Cursor | None:
        """
        Gets the elements which match with `query` from a collection of the database.

        Args:
            collection: The collection of the database.
            query: The query.

        Returns:
            The result of the function `find`.
             If an error occurs, it returns `None`.
        """
        try:
            return self.client[self.database_name][str(collection)].find(query)
        except Exception as error:
            print(error)
            return None

    def __insert_element(self, collection: DBCollections, document: dict) -> results.InsertOneResult | None:
        """
        Inserts an element in a collection of the database.

        Args:
            collection: The collection of the database.
            document: The data to insert.

        Returns:
            The result of the function `insert_one`.
            If an error occurs, it returns `None`.
        """
        try:
            return self.client[self.database_name][str(collection)].insert_one(document)
        except Exception as error:
            print(error)
            return None

    def __update_element(self, collection: DBCollections, query: dict, new_data: dict) -> results.UpdateResult | None:
        """
        Updates an element in a collection of the database.
        The updated element is the first document that matches with `query`.

        Args:
            collection: The collection of the database.
            query: The query.
            new_data: The data to insert. If a data exists, it updates the old data.

        Returns:
            The result of the function `update_one`.
            If an error occurs, it returns `None`.
        """
        try:
            return self.client[self.database_name][str(collection)].update_one(query, {"$set": new_data})
        except Exception as error:
            print(error)
            return None

    def __delete_element(self, collection: DBCollections, query: dict) -> results.DeleteResult | None:
        """
        Deletes an element from a collection of the database.
        The deleted element is the first document that matches with `query`.

        Args:
            collection: The collection of the database.
            query: The query.

        Returns:
            The result of the function `delete_one`.
            If an error occurs, it returns `None`.
        """
        try:
            return self.client[self.database_name][str(collection)].delete_one(query)
        except Exception as error:
            print(error)
            return None

    def __get_clan(self, key: str, value: str) -> dict:
        """
        Returns the clan data of the clan that `key` matches with `value`.

        Args:
            key: the dictionary's key.
            value: The key's value.

        Returns:
            The clan data.
            If an error occurs, it returns an empty dictionary.
        """
        result = self.__get_element(DBCollections.CLANS, {key: value})
        if result:
            return result
        else:
            return {}

    def get_clans(self, key: str, value: str) -> list:
        """
        Return the clans' data of the clans that the value of `key` contains `value`.

        Args:
            key: The dictionary's key.
            value: The key's value.

        Returns:
            A list of clans.
            If no clan was found, it returns an empty list.
        """
        result = self.__get_elements(DBCollections.CLANS, {key: {'$regex': value, '$options': 'i'}})
        if result:
            return list(result)
        else:
            return []

    ####################################################################################################################
    #                                                 PUBLIC API                                                       #
    ####################################################################################################################

    ####################################################################################################################
    #                                                Config file API                                                   #
    ####################################################################################################################
    def get_config(self) -> dict | None:
        """
        Gets the configuration file.

        Returns:
            The configuration file.
        """
        return self.__get_element(DBCollections.CONFIG, {"_id": ObjectId(get_config_id())})

    def update_config(self, config_data: dict) -> results.UpdateResult | None:
        """
        Updates the configuration file.

        Args:
            config_data: The new data to insert. If a key exists, it updates the old data.

        Returns:
            The updated result.
            If an error occurs, it returns `None`.
        """
        return self.__update_element(DBCollections.CONFIG, {"_id": ObjectId(get_config_id())}, {"$set": config_data})

    ####################################################################################################################
    #                                              Clans Collection API                                                #
    ####################################################################################################################
    def get_clan_by_id(self, clan_id: str) -> dict:
        """
        Returns the clan data of the clan that clan's id matches with `clan_id`.

        Args:
            clan_id: The clan id.

        Returns:
            The clan data.
            If an error occurs, it returns an empty dictionary.
        """
        return self.__get_clan("id", clan_id)

    def get_clan_by_tag(self, clan_tag: str) -> dict:
        """
        Returns the clan data of the clan that clan's tag matches with `clan_tag`.

        Args:
            clan_tag: The clan tag.

        Returns:
            The clan data.
            If an error occurs, it returns an empty dictionary.
        """
        return self.__get_clan("tag", clan_tag)

    def get_clan_by_name(self, clan_name: str) -> dict:
        """
        Returns the clan data of the clan that clan's name matches with `clan_name`.

        Args:
            clan_name: The clan name.

        Returns:
            The clan data.
            If an error occurs, it returns an empty dictionary.
        """
        return self.__get_clan("name", clan_name)

    def get_clans_by_id(self, clan_id: str) -> list:
        """
        Returns the clans' data of the clans that id contains `clan_id`.

        Args:
            clan_id: The clan id.

        Returns:
            A list of clans.
            If no clan was found, it returns an empty list.
        """
        return self.get_clans("id", clan_id)

    def get_clans_by_tag(self, clan_tag: str) -> list:
        """
        Returns the clans' data of the clans that tag contains `clan_id`.

        Args:
            clan_tag: The clan tag.

        Returns:
            A list of clans.
            If no clan was found, it returns an empty list.
        """
        return self.get_clans("tag", clan_tag)

    def get_clans_by_name(self, clan_name: str) -> list:
        """
        Returns the clans' data of the clans that name contains `clan_name`.

        Args:
            clan_name: The clan name.

        Returns:
            A list of clans.
            If no clan was found, it returns an empty list.
        """
        return self.get_clans("name", clan_name)

    def insert_clan(self, clan_info: dict) -> results.InsertOneResult | None:
        """
        Inserts a clan in the collection.

        Args:
            clan_info: The data of the clan. It has an "id" (str), a "tag" (str), a "name" (str) and a "representations"
             (list[str]). "representations" is a list of 2 strings.

        Returns:
            the result of the function "__insert_element".
        """
        if self.get_clan_by_id(str(clan_info['id'])) is not None:
            # The clan is already stored
            return None
        r1 = None
        r2 = None
        try:
            r1 = str(clan_info['representations'][0])
            r2 = str(clan_info['representations'][1])
        except Exception as error:
            print(error)
            pass
        return self.__insert_element(
            DBCollections.CLANS,
            {
                'id': str(clan_info['id']),
                'name': str(clan_info['name']),
                'tag': str(clan_info['tag']),
                'representations': [
                    r1,
                    r2
                ]
            })

    def update_clan(self, clan_id: str, clan_data: dict) -> results.UpdateResult | None:
        """
        Update the clan data. The clan to update is the clan that player_id matches with `clan_id`.

        Args:
            clan_id: the clan player_id.
            clan_data: the clan data to insert. If a data exists, it updates the old data.

        Returns:
            the result of the function "__update_element".
        """
        return self.__update_element(DBCollections.CLANS, {'id': clan_id}, clan_data)

    def delete_clan(self, clan_id: str) -> results.DeleteResult | None:
        """
        Delete a clan from the collection. The clan to delete is the clan that player_id matches with `clan_id`.

        Args:
            clan_id: the clan player_id.

        Returns:
            the result of the function "__delete_element".
        """
        return self.__delete_element(DBCollections.CLANS, {'id': clan_id})

    # Player Collection
    def get_player(self, discord_id: str = "", wows_id: str = "") -> dict | None:
        """
        Returns the player's data that discord's id or wows' id matches with `discord_id` or `wows_id`.
        If nothing is matched, it returns `None`.

        Args:
            discord_id: the discord's id.
            wows_id: the wows' id.

        Returns:
            the result of the function "__delete_element".
        """
        query = {
            '$or': [
                {'discord': discord_id},
                {'wows': wows_id}
            ]
        }
        x = self.__get_elements(DBCollections.PLAYERS, query)
        if x:
            return list(x)[0]
        else:
            return None

    def insert_player(self, discord_id: str, wows_id: str, token: str, expire: str) -> results.InsertOneResult | None:
        """
        Search and return a player that discord's id or wows' id matches with the arguments.
        If nothing is matched, it returns `None`.

        Args:
            discord_id: the discord's id.
            wows_id: the wows' id.

        Returns:
            the result of the function "__delete_element".
        """
        player = self.get_player(discord_id, wows_id)
        if player:
            if player["discord_id"] == discord_id:
                print("Discord ID is already in the DB.")
            elif player["wows_id"] == wows_id:
                print("WoWs ID is already in the DB.")
            else:
                print("sus: this should never happens")
            return None
        else:
            inserted_player = self.__insert_element(
                DBCollections.PLAYERS,
                {
                    'discord': discord_id,
                    'wows': wows_id,
                    'token': token,
                    'expire': expire
                }
            )
            if inserted_player:
                if inserted_player.inserted_id:
                    return inserted_player
            return None

    def delete_player(
        self,
        discord_id: str = "",
        wows_id: str = "",
    ) -> results.DeleteResult | None:
        return self.__delete_element(
            DBCollections.PLAYERS,
            {
                '$or': [
                    {'discord': discord_id},
                    {'wows': wows_id}
                ]
            }
        )