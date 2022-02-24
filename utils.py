import requests
from enum import Enum

# Discord's ID
CH_TXT_LOG_EVENT = 681962602657873990
CH_TXT_ADMIN = 696853218642231346
CH_TXT_PODIO_CUP = 818856265237266473
CH_TXT_PODIO_LEAGUE = 779449057600602123
CH_TXT_CLASSIFICA_CB = 847179325349429258
CH_TXT_DEV_BLOG = 696853825247772733

ROLE_ADMIN = 379688107433525271
ROLE_MODERATORE = 539071779247751181
ROLE_CC = 408628827737161728
ROLE_CM = 430713251085418517
ROLE_ORG_LEAGUE = 828669615289663499
ROLE_ORG_CUP = 828669190398935100
ROLE_RAPPRESENTANTE_CLAN = 408630527583846413
ROLE_MARINAIO = 383279930886062082
ROLE_WOWS_ITALIA = 780427147658919946

# Check if the recived data is correct
def checkData(url):
    # send request
    reply = requests.get(url = url)
    data = reply.json()
    # check data errors
    if data['status'] != 'ok':
        print('Status error: ' + data['status'])
        return None
    else:
        return data

# Add white spaces from a side to make the word longs as max characters
def my_align(word, max, side):
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

class Collection(Enum):
    CONFIG = 1
    CLANS = 2

def getConfigId():
    return "6207aa3f69eca41f0736e279"
