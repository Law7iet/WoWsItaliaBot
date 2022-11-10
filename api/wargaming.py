# Documentation: https://developers.wargaming.net/reference/all/wows/account/list/?r_realm=eu&run=1

import json

from config import data
from utils.functions import *


class ApiWargaming:
    def __init__(self):
        self.key = data['APPLICATION_ID']
        self.url_api_root = 'https://api.worldofwarships.eu/wows/'
        self.url_players = self.url_api_root + 'account/list/?application_id=' + self.key + '&search='
        self.url_player_data = self.url_api_root + 'account/info/?application_id=' + self.key + '&account_id='
        self.url_clans = self.url_api_root + 'clans/list/?application_id=' + self.key + '&search='
        self.url_clan_details = self.url_api_root + 'clans/info/?application_id=' + self.key + '&clan_id='
        self.url_player_clan_data = self.url_api_root + 'clans/accountinfo/?application_id=' + self.key + '&account_id='
        self.url_clan_ranking = 'https://clans.worldofwarships.eu/api/clanbase/'

    def get_clan_ranking(self, clan_id: str) -> list:
        """
        Returns the ratings of a clan.
        The ratings are divided by `season_number`.
        Each `season_number` has 2 instance of rating, defined by `team_number` and it represents alpha (1) and bravo
        (2) squad.

        Args:
            clan_id: the clan ID.

        Returns:
            the list of ratings.
        """
        url = self.url_clan_ranking + clan_id + '/claninfo/'
        try:
            # api call
            return json.loads((requests.get(url=url)).text)['clanview']['wows_ladder']['ratings']
        except Exception as error:
            print("ApiWargaming.get_clan_ranking\n" + str(error))
            return []

    def get_player_by_nick(self, nickname: str) -> tuple | None:
        """
        Search the first player whose nickname matches with the parameter and returns its nickname and its ID.

        Args:
            nickname: the nickname.

        Returns:
            it contains the player_id and nickname. If the input nickname doesn't match with any player, it returns
             "None".
        """
        url = self.url_players + nickname
        # api call and check if the response is ok
        response = check_data(url)
        try:
            return response['data'][0]['account_id'], response['data'][0]['nickname']
        except Exception as error:
            print("ApiWargaming.get_player_by_nick\n" + str(error))
            return None

    def get_player_by_id(self, player_id: str) -> tuple | None:
        """
        Search the player whose ID matches with the parameter and returns its nickname and its ID.

        Args:
            player_id: the nickname.

        Returns:
            it contains the player_id and nickname. If the input nickname doesn't match with any player, it returns
             "None".
        """
        url = self.url_player_data + player_id
        # api call and check if the response is ok
        response = check_data(url)
        try:
            return response['data'][player_id]['account_id'], response['data'][player_id]['nickname']
        except Exception as error:
            print("ApiWargaming.get_player_by_id\n" + str(error))
            return None

    def get_clan_by_player_id(self, player_id: str) -> tuple | None:
        """
        Search the player's clan's player_id by the player's ID.

        Args:
            player_id: the ID of the player.

        Returns:
            it contains the clan ID. If the player has not a clan, it returns `None`.
        """
        url = self.url_player_clan_data + player_id
        response = check_data(url)
        try:
            return response['data'][player_id]['clan_id'],
        except Exception as error:
            print("ApiWargaming.get_clan_by_player_by_id\n" + str(error))
            return None

    def get_clan_name_by_id(self, clan_id: str) -> tuple | None:
        """
        Get the clan's name and tag by the clan's ID.

        Args:
            clan_id: the ID of the clan

        Returns:
            it contains the clan name and clan tag. If the ID isn't valid, it returns `None`.
        """
        url = self.url_clan_details + clan_id
        response = check_data(url)
        try:
            return response['data'][clan_id]['name'], response['data'][clan_id]['tag']
        except Exception as error:
            print("ApiWargaming.get_clan_name_by_id\n" + str(error))
            return None
