import requests
from utils.constants import CONFIG_ID

# Some functions
def checkData(url: str) -> dict | None:
    """
    Make an HTTP get request and check if the response is correct, checking the attribute 'status'

    Args:
        `url` (str): the url request.

    Returns:
        `dict` | `None`: the url response. If the request is invalid, it return None.
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

# 
def my_align(word: str, max: int, side: str):
    """
    Add white spaces on a side of a word to make it long as max.

    Args:
        `word` (str): the word.
        `max` (int): the size of the row. If the length of the word is less than max, it returns an empty string.
        `side` (str): the side where you want to add the white spaces; it could be "right" and "left". If side doesn't match, it returns an empty string.

    Returns:
        `str`: it is the word with the white spaces, or an empty string if some error has occured.
    """    
    if len(word) > max:
        return ""
    while len(word) < max:
        if side == "right":
            word = " " + word
        elif side == "left":
            word = word + " "
        else:
            return ""
    return word

def getConfigId():
    return CONFIG_ID