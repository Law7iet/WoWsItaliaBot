import requests
from discord.ext.commands.context import Context

from models.my_enum.roles_enum import RolesEnum
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


async def check_role(ctx: Context, level_role: RolesEnum) -> bool:
    """
    Check if the user has the privileges. The user is the author of the message of the context. The privileges are
 based on server's roles. The roles levels are defined by `RolesEnum` my_class.

    Args:
         ctx: the context.
         level_role: the minimum RolesEnum that the user must have.

     Returns:
         a boolean that states if the user has the permission.
    """
    for index in range(0, int(level_role) + 1):
        role_id = str(RolesEnum(index))
        role = ctx.guild.get_role(int(role_id))
        if role in ctx.message.author.roles:
            return True
    await ctx.message.delete()
    await ctx.send(ctx.message.author.display_name + " non hai i permessi")
    return False


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


def get_maps_reactions(size: int):
    emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣"]
    return emojis[:size]


def get_spawn_reactions():
    return ["🅰️", "🅱️"]
