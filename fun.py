from utils import *
import requests

# Check if the recived data is correct
def check_data(URL):
    # send request
    reply = requests.get(url = URL)
    data = reply.json()
    # check data errors
    if data['status'] != 'ok':
        return 'Status error: ' + data['status']
    else:
        return data

# Get the player's ID from his nickname
def get_player_ID(nickname):
    # get player ID
    URL = URL_PLAYER_ID + nickname
    # check data errors
    data = check_data(URL)
    try:
        data = data['data']
        data.reverse()
        data = data.pop()
        return [data['nickname'], data['account_id']]
    except:
        return -1

# Get the player's clan's ID from his ID
def get_clan_ID(ID):
    # get clan ID
    URL = URL_PLAYER_CLAN_ID + str(ID)
    # check data errors
    data = check_data(URL)
    data = data['data']
    if data[str(ID)]['clan_id'] == None:
        return -1
    else:
        return data[str(ID)]['clan_id']

# Get the clan's name form its ID
def get_clan_name(ID):
    # get clan name
    URL = URL_CLAN_NAME + str(ID)
    # check data errors
    data = check_data(URL)
    data = data['data']
    if data[str(ID)]['tag'] != None:
        return data[str(ID)]['tag']

def my_align(word, max, side):
    if len(word) > max:
        return ""
    else:
        while len(word) < max:
            if side == "right":
                word = " " + word
            elif side == "left":
                word = word + " "
            else:
                return ""
        return word


