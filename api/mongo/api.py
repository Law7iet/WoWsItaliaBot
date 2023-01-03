# Documentation: https://www.mongodb.com/languages/python

from bson import ObjectId
from pymongo import MongoClient, errors

from api.mongo.utils import DBCollections
from settings.config import data
from utils.functions import get_config_id


class ApiMongoDB:
    def __init__(self):
        self.project = "WoWsItaliaBot"
        self.database_name = "WoWsItalia"
        try:
            self.client = MongoClient(serverSelectionTimeoutMS=10)
            self.client = MongoClient(f"mongodb+srv://{data['MONGO_USER']}:{data['MONGO_PASSWORD']}@cluster0.rtvit"
                                      f".mongodb.net/{self.project}?retryWrites=true&w=majority")
        except (errors.ConnectionFailure, errors.ServerSelectionTimeoutError):
            raise Exception("Database non connesso")

    ####################################################################################################################
    #                                                   PRIVATE API                                                    #
    ####################################################################################################################
    # Parametric API to mongo
    def __get_element(self, collection: DBCollections, query: dict) -> dict:
        """
        Gets an element which matches with `query` from a collection of the database.

        Args:
            collection: The collection of the database.
            query: The query.

        Returns:
            A dictionary represents the result of the function `find_one`.
             If an error occurs, it returns an empty dictionary.
        """
        try:
            return self.client[self.database_name][str(collection)].find_one(query)
        except Exception as error:
            print(f"Error: Mongo __get_element({str(DBCollections)}, {query})\n{error}")
            return {}

    def __get_elements(self, collection: DBCollections, query: dict) -> list:
        """
        Gets the elements which match with `query` from a collection of the database.

        Args:
            collection: The collection of the database.
            query: The query.

        Returns:
            A list of elements.
             If an error occurs, it returns an empty list.
        """
        try:
            return list(self.client[self.database_name][str(collection)].find(query))
        except Exception as error:
            print(f"Error: Mongo __get_elements({str(DBCollections)}, {query})\n{error}")
            return []

    def __insert_element(self, collection: DBCollections, document: dict) -> dict:
        """
        Inserts an element in a collection of the database.

        Args:
            collection: The collection of the database.
            document: The data to insert.

        Returns:
            The inserted document.
             If an error occurs or if the document is not inserted, it returns an empty dictionary.
        """
        try:
            insertedDocument = self.client[self.database_name][str(collection)].insert_one(document)
            document["_id"] = insertedDocument.inserted_id
            return document
        except errors.DuplicateKeyError:
            print(f"Error: Mongo __insert_element({str(DBCollections)}, {document})\nDuplicated Key")
        except errors.WriteError as error:
            if error.code == 121:
                print(f"Error: Mongo __insert_element({str(DBCollections)}, {document})\nInvalid schema")
            else:
                print(f"Error: Mongo __insert_element({str(DBCollections)}, {document})\n{error}")
        except Exception as error:
            print(f"Error: Mongo __insert_element({str(DBCollections)}, {document})\n{error}")
        return {}

    def __update_element(self, collection: DBCollections, query: dict, new_data: dict) -> dict:
        """
        Updates an element in a collection of the database.
        The updated element is the first document that matches with `query`.

        Args:
            collection: The collection of the database.
            query: The query.
            new_data: The data to insert. If a data exists, it updates the old data.

        Returns:
            The updated document.
             If an error occurs or if the document is not found, it returns an empty
             dictionary.
        """
        try:
            elementToUpdate = self.client[self.database_name][str(collection)].find_one(query)
            updatedResult = self.client[self.database_name][str(collection)].update_one(query, {"$set": new_data})
            match updatedResult.matched_count:
                case 0:
                    if updatedResult.modified_count == 0:
                        return {}
                    else:
                        msg = f"matched_count is 0 but modified_count is not 0, it's {updatedResult.modified_count}"
                        raise Exception(msg)
                case 1:
                    return elementToUpdate | new_data
                case _:
                    msg = f"Warning: Mongo __update_element({str(DBCollections)}, {query}, {new_data})\n"
                    msg = msg + f"Matched count is higher than 1, it's {updatedResult.matched_count}"
                    print(msg)
                    if updatedResult.modified_count == 1:
                        return elementToUpdate | new_data
                    else:
                        msg = f"matched_count is {updatedResult.matched_count} but modified_count is not 0, "
                        msg = msg + f"it's {updatedResult.modified_count}"
                        raise Exception(msg)
        except errors.WriteError as error:
            msg = f"Error: Mongo __update_element({str(DBCollections)}, {query}, {new_data})\n"
            match error.code:
                case 66:
                    print(msg + "Update immutable _id")
                case 121:
                    print(msg + "Invalid schema")
                case _:
                    print(msg + f"{error}")
            return {}
        except Exception as error:
            print(f"Error: Mongo __update_element({str(DBCollections)}, {query}, {new_data})\n{error}")
            return {}

    def __delete_element(self, collection: DBCollections, query: dict) -> dict:
        """
        Deletes an element from a collection of the database.
        The deleted element is the first document that matches with `query`.

        Args:
            collection: The collection of the database.
            query: The query.

        Returns:
            The deleted document.
             If an error occurs, or if the document is not found it returns an empty dictionary.
        """
        try:
            elementToDelete = self.client[self.database_name][str(collection)].find_one(query)
            deletedResult = self.client[self.database_name][str(collection)].delete_one(query)
            if deletedResult.deleted_count == 0:
                return {}
            elif deletedResult.deleted_count == 1:
                return elementToDelete
            else:
                msg = f"Warning: Mongo __delete_element({str(DBCollections)}, {query})"
                raise Exception(msg + f"\nMatched count {deletedResult.deleted_count}")
        except Exception as error:
            print(error)
            return {}

    def __get_clan(self, key: str, value: str) -> dict:
        """
        Returns the clan's data of the clan that its `key` matches with `value`.

        Args:
            key: The dictionary's key.
            value: The key's value.

        Returns:
            The clan's data.
             If an error occurs or if no clan is found, it returns an empty dictionary.
        """
        return self.__get_element(DBCollections.CLANS, {key: value})

    def __get_clans(self, key: str, value: str) -> list:
        """
        Returns the clan's data of the clans that its `key` contains `value`.

        Args:
            key: The dictionary's key.
            value: The key's value.

        Returns:
            A list of clans.
             If no clan is found, it returns an empty list.
        """
        return self.__get_elements(DBCollections.CLANS, {key: {'$regex': value, '$options': 'i'}})

    def __get_player(self, query: dict) -> dict:
        """
        Returns the player's data that match with `query`.

        Args:
            query: The query.

        Returns:
            The player data.
             If an error occurs or if no player is found, it returns an empty dictionary.
        """
        return self.__get_element(DBCollections.PLAYERS, query)

    ####################################################################################################################
    #                                                    PUBLIC API                                                    #
    ####################################################################################################################

    ####################################################################################################################
    #                                                 Config file API                                                  #
    ####################################################################################################################
    def get_config(self) -> dict:
        """
        Gets the configuration file.

        Returns:
            The configuration file.
        """
        return self.__get_element(DBCollections.CONFIG, {"_id": ObjectId(get_config_id())})

    def update_config(self, config_data: dict) -> dict:
        """
        Updates the configuration file.

        Args:
            config_data: The new data to insert. If a key exists, it updates the old data.

        Returns:
            The updated result.
             If an error occurs, it returns an empty dictionary.
        """
        return self.__update_element(DBCollections.CONFIG, {"_id": ObjectId(get_config_id())}, config_data)

    ####################################################################################################################
    #                                             Clans Collection API                                                 #
    ####################################################################################################################
    def get_clan_by_id(self, clan_id: str) -> dict:
        """
        Returns the clan's data of the clan that its id matches with `clan_id`.

        Args:
            clan_id: The clan's id.

        Returns:
            The clan's data.
             If the clan is not found or if an error occurs, it returns an empty dictionary.
        """
        return self.__get_clan("id", clan_id)

    def get_clan_by_tag(self, clan_tag: str) -> dict:
        """
        Returns the clan's data of the clan that its tag matches with `clan_tag`.

        Args:
            clan_tag: The clan's tag.

        Returns:
            The clan's data.
             If the clan is not found or if an error occurs, it returns an empty dictionary.
        """
        return self.__get_clan("tag", clan_tag)

    def get_clan_by_name(self, clan_name: str) -> dict:
        """
        Returns the clan's data of the clan that its name matches with `clan_name`.

        Args:
            clan_name: The clan's name.

        Returns:
            The clan's data.
             If the clan is not found or if an error occurs, it returns an empty dictionary.
        """
        return self.__get_clan("name", clan_name)

    def get_clans_by_id(self, clan_id: str) -> list:
        """
        Returns the clan's data of the clans that their id contains `clan_id`.

        Args:
            clan_id: The clan's id.

        Returns:
            A list of clans.
             If no clan is found or if an error occurs, it returns an empty dictionary.
        """
        return self.__get_clans("id", clan_id)

    def get_clans_by_tag(self, clan_tag: str) -> list:
        """
        Returns the clan's data of the clans that their tag contains `clan_tag`.

        Args:
            clan_tag: The clan's tag.

        Returns:
            A list of clans.
             If no clan is found or if an error occurs, it returns an empty dictionary.
        """
        return self.__get_clans("tag", clan_tag)

    def get_clans_by_name(self, clan_name: str) -> list:
        """
        Returns the clan's data of the clans that name contains `clan_name`.

        Args:
            clan_name: The clan name.

        Returns:
            A list of clans.
             If no clan is found or if an error occurs, it returns an empty dictionary.
        """
        return self.__get_clans("name", clan_name)

    def insert_clan(self, clan_info: dict) -> dict:
        """
        Inserts a clan in the collection.

        Args:
            clan_info: The data of the clan.

        Returns:
            The inserted clan with its `_id`.
             If the clan is already stored or if an error occurs, it returns an empty dictionary.
        """
        if not self.get_clan_by_id(str(clan_info["id"])):
            representations = []
            try:
                representations.append(str(clan_info["representations"][0]))
            except (KeyError, IndexError):
                pass
            try:
                representations.append(str(clan_info["representations"][1]))
            except (KeyError, IndexError):
                pass
            return self.__insert_element(
                DBCollections.CLANS,
                {
                    "id": str(clan_info["id"]),
                    "name": str(clan_info["name"]),
                    "tag": str(clan_info["tag"]),
                    "representations": representations
                })
        else:
            return {}

    def update_clan_by_id(self, clan_id: str, clan_data: dict) -> dict:
        """
        Updates the clan's data.
        The clan to update is the clan that its id matches with `clan_id`.

        Args:
            clan_id: The clan's id.
            clan_data: The clan's data to update. If a data doesn't exist, it inserts the new data.

        Returns:
            The updated clan.
             If the clan is not found or if an error occurs, it returns an empty dictionary.
        """
        return self.__update_element(DBCollections.CLANS, {"id": clan_id}, clan_data)

    def delete_clan_by_id(self, clan_id: str) -> dict:
        """
        Deletes a clan from the collection.
        The clan to delete is the clan that its id matches with `clan_id`.

        Args:
            clan_id: The clan's id.

        Returns:
            The deleted clan.
             If the clan is not found or if an error occurs, it returns an empty dictionary.
        """
        return self.__delete_element(DBCollections.CLANS, {"id": clan_id})

    ####################################################################################################################
    #                                              Player Collection API                                               #
    ####################################################################################################################
    def get_player(self, discord_id: str, wows_id: str) -> dict:
        """
        Returns the player's data that Discord's id and WoWs' id matches with `discord_id` and `wows_id`.

        Args:
            discord_id: the Discord's id.
            wows_id: the WoWs' id.

        Returns:
            The player data.
             If the player is not found or if an error occurs, it returns an empty dictionary.
        """
        return self.__get_player({"$and": [{"discord": discord_id}, {"wows": wows_id}]})

    def get_player_by_discord(self, discord_id: str) -> dict:
        """
        Returns the player's data that Discord's id matches with `discord_id`.

        Args:
            discord_id: the Discord's id.

        Returns:
            The player data.
             If the player is not found or if an error occurs, it returns an empty dictionary.
        """
        return self.__get_player({"discord": discord_id})

    def get_player_by_wows(self, wows_id: str) -> dict:
        """
        Returns the player's data that WoWs' id matches with `wows_id`.

        Args:
            wows_id: the WoWs' id.

        Returns:
            The player data.
             If the player is not found or if an error occurs, it returns an empty dictionary.
        """
        return self.__get_player({"wows": wows_id})

    def insert_player(self, discord_id: str, wows_id: str, token: str = "", expire: str = "") -> dict:
        """
        Inserts a player in the collection.

        Args:
            discord_id: The Discord's id of the player.
            wows_id: The WoWs' id of the player.
            token: The token to access the personal data of the wargaming API.
            expire: The date of the token's expire.

        Returns:
            The inserted player.
             If the player is already stored or if an error occurs, it returns an empty dictionary.
        """
        player = self.get_player(discord_id, wows_id)
        if not player:
            return self.__insert_element(
                DBCollections.PLAYERS,
                {
                    "discord": discord_id,
                    "wows": wows_id,
                    "token": token,
                    "expire": expire
                }
            )
        else:
            return {}

    def update_player(self, discord_id: str, player_data: dict) -> dict:
        """
        Updates the player's data.
        The player to update is the player that its Discord's id matches with `discord_id`.

        Args:
            discord_id: The Discord's id of the player.
            player_data: The player's data to update. If a data doesn't exist, it inserts the new data.

        Returns:
            The inserted player.
             If the player is not found or if an error occurs, it returns an empty dictionary.
        """
        return self.__update_element(DBCollections.PLAYERS, {"discord": discord_id}, player_data)

    def delete_player(self, discord_id: str, wows_id: str) -> dict:
        """
        Deletes a player from the collection.
        The player to delete is the player that its Discord's and WoWs' id matches with `discord_id` and `clan_id`.

        Args:
            discord_id: The Discord's id of the player.
            wows_id: The WoWs' id of the player.

        Returns:
            The deleted player.
             If the player is not found or if an error occurs, it returns an empty dictionary.
        """
        return self.__delete_element(
            DBCollections.PLAYERS,
            {'$and': [
                {'discord': discord_id},
                {'wows': wows_id}
            ]}
        )
		