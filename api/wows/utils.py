from enum import Enum

import requests


class ShipType(str, Enum):
    DD = "Destroyer"
    CA = "Cruiser"
    BB = "Battleship"
    CV = "AirCarrier"


def check_data(url: str) -> dict:
    """
    Make an HTTP get request to Wargaming and check if the response is correct.
    The request is fine if `status` is `ok`.

    Args:
        url: the url request.

    Returns:
        the url response. If the request is invalid, it throws an exception.
    """
    # send request
    reply = requests.get(url=url)
    data = reply.json()
    # check data errors
    if data['status'] != 'ok':
        raise Exception(data["error"])
    else:
        return data["data"]


def clear_dict_to_list(data: dict) -> list:
    """
    Remove the empty values from the passed dictionary and covert the dictionary to a list removing the keys.

    Args:
        data: the data.

    Returns:
        a list. If the request is invalid, it returns an empty list.
    """
    filtered = {k: v for k, v in data.items() if v is not None}
    if filtered:
        return list(filtered.values())
    else:
        return []
