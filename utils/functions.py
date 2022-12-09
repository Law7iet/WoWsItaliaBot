import sys
import asyncio
import datetime
from typing import Union

import requests
from disnake import ApplicationCommandInteraction, ModalInteraction, Role

from utils.constants import CONFIG_ID
from models.my_enum.roles_enum import RolesEnum


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


async def check_role(inter: ApplicationCommandInteraction, value: RolesEnum) -> bool:
    role = inter.guild.get_role(value)
    if role in inter.author.roles:
        return True
    else:
        return False


async def send_response_and_clear(
        inter: Union[ApplicationCommandInteraction, ModalInteraction],
        defer: bool,
        text: str = "Done"
) -> None:
    if defer is True:
        await inter.send(text)
    else:
        await inter.response.send_message(text)
    await asyncio.sleep(5)
    message = await inter.original_message()
    await message.delete()


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


def convert_string_to_datetime(string: str) -> datetime.datetime:
    x = string.split('-')
    return datetime.datetime(int(x[0]), int(x[1]), int(x[2]))


def is_debugging() -> bool:
    if sys.gettrace() is None:
        return False
    else:
        return True
