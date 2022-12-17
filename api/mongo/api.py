# Documentation: https://www.mongodb.com/languages/python

from bson import ObjectId
from pymongo import MongoClient, cursor, results

from models.my_enum.database_enum import DBCollections
# from settings import config
from utils.functions import get_config_id


class ApiMongoDB:
    def __init__(self):
        # self.database_name = 'WoWsItaliaBotDB'
        self.database_name = "WoWsItaliaDB"

        # self.client = MongoClient('mongodb+srv://' + config.data['MONGO_USER'] + ':' + config.data[
        #     'MONGO_PASSWORD'] + '@cluster0.rtvit.mongodb.net/' + self.project + '?retryWrites=true&w=majority')
        self.client = MongoClient()

    # Private API
    # Parametric API to mongo
    def __get_element(self, collection: DBCollections, query: dict) -> any:
        """
        Get an element which matches with `query` from a collection of the database.
        If an error occurs, it returns `None`.

        Args:
            collection: it states which collection the function is using.
            query: the query.

        Returns:
            the result of the function find_one. If an error occurs, it returns None.
        """
        try:
            return self.client[self.database_name][str(collection)].find_one(query)
        except Exception as error:
            print(error)
            return None

    def __get_elements(self, collection: DBCollections, query: dict) -> cursor.Cursor | None:
        """
        Get elements which match with `query` from a collection of the database.
        If an error occurs, it returns `None`.

        Args:
            `collection` (DatabaseCollection): it states which collection the function is using.
            `query` (dict): the query.

        Returns:
            `cursor.Cursor` | `None`: the result of the function `find`. If an error occurs, it returns `None`.
        """
        try:
            return self.client[self.database_name][str(collection)].find(query)
        except Exception as error:
            print(error)
            return None

    def __insert_element(self, collection: DBCollections, document: dict) -> results.InsertOneResult | None:
        """
        Insert an element in a collection of the database.
        If an error occurs, it returns `None`.

        Args:
            collection: it states which collection the function is using.
            document: the data to insert.

        Returns:
            the result of the function "insert_one". If an error occurs, it returns "None".
        """
        try:
            return self.client[self.database_name][str(collection)].insert_one(document)
        except Exception as error:
            print(error)
            return None

    def __update_element(self, collection: DBCollections, query: dict,
                         new_data: dict) -> results.UpdateResult | None:
        """
        Update an element in a collection of the database. The element is the first document that matches with `query`.
        If an error occurs, it returns `None`.

        Args:
            collection: it states which collection the function is using.
            query: the query.
            new_data: the data to insert. If a data exists, it updates the old data.

        Returns:
            the result of the function "update_one". If an error occurs, it returns "None".
        """
        try:
            return self.client[self.database_name][str(collection)].update_one(query, new_data)
        except Exception as error:
            print(error)
            return None

    def __delete_element(self, collection: DBCollections, query: dict) -> results.DeleteResult | None:
        """
        Delete an element from a collection of the database. The element is the first document that matches with
        `query`. If an error occurs, it returns `None`.

        Args:
            collection: it states which collection the function is using.
            query: the query.

        Returns:
            the result of the function "delete_one". If an error occurs, it returns "None".
        """
        try:
            return self.client[self.database_name][str(collection)].delete_one(query)
        except Exception as error:
            print(error)
            return None

    # Public API
    # Config file API
    def get_config(self) -> any:
        """
        Get the configuration file.

        Returns:
            the result of the function "__get_element".
        """
        return self.__get_element(DBCollections.CONFIG, {'_id': ObjectId(get_config_id())})

    def update_config(self, config_data: dict) -> results.UpdateResult | None:
        """
        Update the configuration file.

        Args:
            config_data: the data to insert. If a data exists, it updates the old data.

        Returns:
            the result of the function "__update_element".
        """
        return self.__update_element(
            DBCollections.CONFIG, {'_id': ObjectId(get_config_id())}, {'$set': config_data})

    # Clans Collection API
    def get_clan_by_id(self, clan_id: str) -> any:
        """
        Return the clan data of the clan that player_id matches with `clan_id`.

        Args:
            clan_id: the clan player_id.

        Returns:
            the result of the function "__get_element". If no clan was found, it returns "None".
        """
        return self.__get_element(DBCollections.CLANS, {'id': clan_id})

    def get_clans_by_tag(self, clan_tag: str) -> list | None:
        """
        Return the clans' data of the clans that tag contains `clan_tag`.

        Args:
            clan_tag: the clan tag.

        Returns:
            the result of the function "__get_elements" cast to a "list". If no clan was found, it returns "None".
        """
        x = self.__get_elements(DBCollections.CLANS, {'tag': {'$regex': clan_tag, '$options': 'i'}})
        if x:
            return list(x)
        else:
            return None

    def get_clans_by_name(self, clan_name: str) -> list | None:
        """
        Return the clans' data of the clans that name contains `clan_tag`.

        Args:
            clan_name: the clan name.

        Returns:
            the result of the function "__get_elements" cast to a "list". If no clan was found, it returns "None".
        """
        x = self.__get_elements(DBCollections.CLANS, {'name': {'$regex': clan_name, '$options': 'i'}})
        if x:
            return list(x)
        else:
            return None

    def insert_clan(self, clan_info: dict) -> results.InsertOneResult | None:
        """
        Insert a clan in the collection.

        Args:
            clan_info: the data of the clan. It has an "id" (str), a "tag" (str), a "name" (str) and a
             "representations" (list[str]). "representations" is a list of 2 strings.

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
        return self.__update_element(DBCollections.CLANS, {'player_id': clan_id}, clan_data)

    def delete_clan(self, clan_id: str) -> results.DeleteResult | None:
        """
        Delete a clan from the collection. The clan to delete is the clan that player_id matches with `clan_id`.

        Args:
            clan_id: the clan player_id.

        Returns:
            the result of the function "__delete_element".
        """
        return self.__delete_element(DBCollections.CLANS, {'player_id': clan_id})

    def get_player(self, discord_id: str = "", wows_id: str = "") -> list | None:
        query = {'$or': [
            {'discord': discord_id},
            {'wows': wows_id}
        ]}
        x = self.__get_elements(DBCollections.PLAYERS, query)
        if x:
            return list(x)
        else:
            return None

    def insert_player(
        self,
        discord_id: str,
        wows_id: str,
        token: str,
        expire: str
    ) -> results.InsertOneResult | None:
        player = self.get_player(discord_id, wows_id)
        if player:
            player = player[0]
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