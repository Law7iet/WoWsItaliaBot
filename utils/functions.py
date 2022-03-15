import requests
from utils.constants import CONFIG_ID


def check_data(url: str) -> dict | None:
    """
    Make an HTTP get request and check if the response is correct, checking the attribute `status`.

    Args:
        url: the url request.

    Returns:
        the url response. If the request is invalid, it return "None".
    """
    # send request
    reply = requests.get(url=url)
    data = reply.json()
    # check data errors
    if data['status'] != 'ok':
        print('Status error: ' + data['status'])
        return None
    else:
        return data


def my_align(word: str, max_length: int, side: str) -> str:
    """
    Add white spaces on a side of a word to make it long as max.

    Args:
        word: the word.
        max_length: the size of the row. If the length of the word is less than max, it returns an empty string.
        side: the side where you want to add the white spaces; it could be "right" and "left". If side doesn't match,
         it returns an empty string.

    Returns:
        it is the word with the white spaces, or an empty string if some error has occurred.
    """
    if len(word) > max_length:
        return ""
    while len(word) < max_length:
        if side == "right":
            word = " " + word
        elif side == "left":
            word = word + " "
        else:
            return ""
    return word


def get_config_id() -> str:
    return CONFIG_ID
