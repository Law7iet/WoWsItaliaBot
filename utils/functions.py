import asyncio
import datetime
import re
import sys
from typing import TYPE_CHECKING, Union

import requests
from disnake import ApplicationCommandInteraction, ModalInteraction, errors

from models.my_enum.roles_enum import RolesEnum
from utils.constants import CONFIG_ID

if TYPE_CHECKING:
    from api.mongo.api import ApiMongoDB
    from api.wows.api import WoWsSession


def check_data(url: str) -> dict | None:
    """
    Make an HTTP get request and check if the response is correct, checking the attribute `status`.

    Args:
        url: the url request.

    Returns:
        the url response. If the request is invalid, it returns "None".
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
    role = inter.guild.get_role(int(value))
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


async def logout(inter: ApplicationCommandInteraction, mongo: "ApiMongoDB") -> None:
    await inter.response.defer()
    if not await check_role(inter, RolesEnum.AUTH):
        await inter.send("Utente non autenticato.")
    else:
        player = mongo.get_player_by_discord(str(inter.author.id))
        deleted_player = mongo.delete_player(player["discord"], player["wows"])
        if deleted_player:
            # Remove role, restore nickname and clean DB
            if inter.guild.get_role(int(RolesEnum.AUTH)) in inter.author.roles:
                await inter.author.remove_roles(inter.guild.get_role(int(RolesEnum.AUTH)))
            if inter.guild.get_role(int(RolesEnum.REP)) in inter.author.roles:
                await inter.author.remove_roles(inter.guild.get_role(int(RolesEnum.REP)))
                clan_tag = re.search(r"\[.+]", inter.author.display_name).group(0)[1:-1]
                clan_data = mongo.get_clan_by_tag(clan_tag)
                representations = clan_data["representations"]
                representations.remove(str(inter.author.id))
                res = mongo.update_clan_by_id(clan_data["id"], {"representations": representations})
                if not res:
                    msg = "Errore durante l'aggiornamento del clan. Controllare il terminale e/o log."
                    await inter.channel.send(msg)
            try:
                await inter.author.edit(nick=None)
            except errors.Forbidden:
                pass
            await inter.send("Logout effettuato con successo.")
        else:
            await inter.send("Logout non effettuato.")


async def check_clan(
        inter: ApplicationCommandInteraction,
        mongo: "ApiMongoDB",
        wows: "WoWsSession",
        clan_id: str
) -> dict:
    clan_mongo = mongo.get_clan_by_id(clan_id)
    clan_wows = wows.clan_detail([clan_id])[0]
    representants = clan_mongo["representations"]
    tag = clan_wows["tag"]
    updates = {}
    if clan_mongo["name"] != clan_wows["name"]:
        updates["name"] = clan_wows["name"]
    if clan_mongo["tag"] != tag:
        updates["tag"] = tag
    if updates:
        # Update clan
        updated_clan = mongo.update_clan_by_id(clan_id, updates)
        # Update representants' tag
        for representant in representants:
            member = inter.guild.get_member(representant)
            nickname = member.display_name
            nickname = re.sub(r"\[.+]", "", nickname).rstrip()
            nickname = f"[{tag}] {nickname}"
            if len(nickname) >= 32:
                nickname = re.sub(r"\(.+\)", "", nickname).lstrip()
            await member.edit(nick=nickname)
        return updated_clan
    else:
        return clan_mongo
