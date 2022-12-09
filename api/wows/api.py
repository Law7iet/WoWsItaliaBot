import json

import requests

from api.wows.urls import URL_ROOT, PLAYERS, PLAYER_CLAN_DATA, WARSHIPS, CLANS, CLANS_DETAIL, CB_RANKING
from api.wows.utils import ShipType, check_data, clear_dict_to_list


def cb_ranking(clan_id: int, debugging: bool) -> list:
    """
    Returns the ratings of a clan.
    The ratings are divided by `season_number`.
    Each `season_number` has 2 instance of rating, defined by `team_number` and it represents alpha (1) and bravo
    (2) squad.

    Args:
        clan_id: the clan ID.
        debugging: a value that states if it's debugging

    Returns:
        the list of ratings.
    """
    url = CB_RANKING + str(clan_id) + "/claninfo/"
    if debugging:
        print(url)
    try:
        # api call
        return json.loads((requests.get(url=url)).text)['clanview']['wows_ladder']['ratings']
    except Exception as error:
        print("get_clan_ranking\n" + str(error))
        return []


class WoWsSession:
    def __init__(self, application_id: str, debugging: bool):
        self.app_id = application_id
        self.debugging = debugging

    def players(self, search: str) -> list:
        """
        Search a player.

        Args:
            self: the context.
            search: the player's nickname.

        Returns:
            a list with the players' main information that match with the search. If an error occurs it returns an empty
            list.
        """
        if not search:
            print("input is empty")
            return []
        if search.find(" ") != -1:
            print("search has whitespace")
            return []
        url = URL_ROOT + PLAYERS + "?application_id=" + self.app_id + "&search=" + search
        if self.debugging:
            print(url)
        try:
            data = check_data(url)
            return list(data)
        except Exception as error:
            print(error)
            return []

    def player_personal_data(self, accounts_id: [int], access_token: str = None) -> list:
        """
        Get a players' data.

        Args:
            self: the context.
            accounts_id: the players' id.
            access_token: a token used to show private data.

        Returns:
            a list with the players' data. If an error occurs it returns ad empty list.
        """
        url = URL_ROOT + PLAYER_CLAN_DATA + "?application_id=" + self.app_id
        if accounts_id:
            url = url + "&account_id=" + "%2C+".join(str(x) for x in accounts_id)
        else:
            print("Empty input")
            return []
        if access_token:
            # TODO manage access_token to get private's data
            print(access_token)
        if self.debugging:
            print(url)
        try:
            data = check_data(url)
            return clear_dict_to_list(data)
        except Exception as error:
            print(error)
            return []

    def warships(self, ships_id: [int] = None, types: [ShipType] = None) -> list:
        """
        Get a list of ships. If ships_id is empty, it requests all the ships.

        Args:
            self: the context.
            ships_id: a list of the ships' id.
            types: a list of the ships' type.

        Returns:
            a list with the ships' data. If an error occurs it returns an empty list.
        """
        url = URL_ROOT + WARSHIPS + "?application_id=" + self.app_id
        if ships_id:
            url = url + "&ship_id=" + "%2C+".join(str(x) for x in ships_id)
        if types:
            url = url + "&type=" + "%2C+".join(types)
        if self.debugging:
            print(url)
        try:
            data = check_data(url)
            return clear_dict_to_list(data)
        except Exception as error:
            print(error)
            return []

    def clans(self, search: str) -> list:
        """
        Search a clan.

        Args:
            self: the context.
            search: the clan's name.

        Returns:
            a list with the clans' main information that match with the search. If an error occurs it returns an empty
            list.
        """
        url = URL_ROOT + CLANS + "?application_id=" + self.app_id
        if search:
            url = url + "&search=" + search
        if self.debugging:
            print(url)
        try:
            data = check_data(url)
            return list(data)
        except Exception as error:
            print(error)
            return []

    def clan_detail(self, clans_id: [int]) -> list:
        """
        Get a list of clans' details.

        Args:
            self: the context.
            clans_id: a list of the clans' id.

        Returns:
            a list with the clans' data. If an error occurs it returns an empty list.
        """
        url = URL_ROOT + CLANS_DETAIL + "?application_id=" + self.app_id
        if clans_id:
            url = url + "&clan_id=" + "%2C+".join(str(x) for x in clans_id)
        else:
            print("Empty input")
            return []
        if self.debugging:
            print(url)
        try:
            data = check_data(url)
            return clear_dict_to_list(data)
        except Exception as error:
            print(error)
            return []

    def player_clan_data(self, accounts_id: [int]):
        """
        Get a list of players' clans-details.

        Args:
            self: the context.
            accounts_id: a list of the players' id.

        Returns:
            a list with the players' data. If an error occurs it returns an empty list.
        """
        url = URL_ROOT + PLAYER_CLAN_DATA + "?application_id=" + self.app_id
        if accounts_id:
            url = url + "&account_id=" + "%2C+".join(str(x) for x in accounts_id)
        else:
            print("empty input")
            return []
        if self.debugging:
            print(url)
        try:
            data = check_data(url)
            return clear_dict_to_list(data)
        except Exception as error:
            print(error)
            return []

    # TODO Look at RapaxBot API
