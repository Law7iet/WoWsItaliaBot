import datetime
import re
import sys
from typing import TYPE_CHECKING

import requests
from disnake import ApplicationCommandInteraction, errors, Member, Role

from models.enum.discord_id import MyRoles
from utils.constants import CONFIG_ID

if TYPE_CHECKING:
    from api.mongo.api import ApiMongoDB
    from api.wows.api import WoWsSession

# TODO: Add docstring to the functions


def align(word: str, max_length: int, side: str) -> str:
    """
    Add white spaces on a side of a word to make it long as max.

    Args:
        word: The word.
        max_length: The size of the row. If the length of the word is less than max, it returns an empty string.
        side: The side where you want to add the white spaces; it could be "right" and "left". If side doesn't match,
         it returns an empty string.

    Returns:
        It is the word with the white spaces, or an empty string if some error has occurred.
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


async def sync_clan(
        inter: ApplicationCommandInteraction,
        mongo: "ApiMongoDB",
        wows: "WoWsSession",
        clan_id: str
) -> dict:
    """
    Synchronize the clan's data between the WoWs' API and MongoDB's data.
    If the tag is changed, it updates the tag of his representations.

    Args:
        inter: The contex.
        mongo: Mongo API.
        wows: WoWs API.
        clan_id: The clan identifier.

    Returns:
        The synchronized and updated clan's data of MongoDB.
    """
    clan_mongo = mongo.get_clan_by_id(clan_id)
    clan_wows = wows.clan_detail([clan_id])[0]
    representations = clan_mongo["representations"]
    tag = clan_wows["tag"]
    updates = {}
    if clan_mongo["name"] != clan_wows["name"]:
        updates["name"] = clan_wows["name"]
    if clan_mongo["tag"] != tag:
        updates["tag"] = tag
    if updates:
        # Update clan
        updated_clan = mongo.update_clan_by_id(clan_id, updates)
        if updated_clan:
            # Clan correctly updated
            # Update representations' tag
            for representant in representations:
                member = inter.guild.get_member(int(representant))
                nickname = re.sub(r"\[.+]", "", member.display_name).rstrip()
                nickname = f"[{tag}] {nickname}"
                try:
                    await member.edit(nick=nickname)
                except errors.Forbidden:
                    msg = f"`sync_clan(inter, mongo, wows, {clan_id})` exceptions sasys:\n"
                    msg = msg + f"Errore durante l'aggiornamento del nickname di <@{member.id}>"
                    await inter.channel.send(msg)
            return updated_clan
        else:
            # Clan not correctly updated
            msg = f"`sync_clan(inter, mongo, wows, {clan_id})` exceptions sasys:\n"
            msg = msg + f"Errore durante l'aggiornamento del clan {clan_id}. Controllare il terminale e/o log."
            await inter.channel.send(msg)
    else:
        # No updates
        return clan_mongo


def check_data(url: str) -> dict | None:
    """
    Make an HTTP get request and check if the response is correct, checking the attribute `status`.

    Args:
        url: The url request.

    Returns:
        The url response. If the request is invalid, it returns "None".
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


async def check_role(inter: ApplicationCommandInteraction, value: MyRoles, member: Member = None) -> bool:
    role = inter.guild.get_role(int(value))
    user = member if member else inter.author
    if role in user.roles:
        return True
    else:
        return False


def convert_string_to_datetime(string: str) -> datetime.datetime:
    x = string.split('-')
    return datetime.datetime(int(x[0]), int(x[1]), int(x[2]))


def get_config_id() -> str:
    return CONFIG_ID


def is_debugging() -> bool:
    if sys.gettrace() is None:
        return False
    else:
        return True


async def logout(inter: ApplicationCommandInteraction, mongo: "ApiMongoDB") -> None:
    await inter.response.defer()
    if not await check_role(inter, MyRoles.AUTH):
        await inter.send(f"Logout non effettuato: utente <@{inter.author.id}> non autenticato.")
    else:
        player = mongo.get_player_by_discord(str(inter.author.id))
        deleted_player = mongo.delete_player(player["discord"], player["wows"])
        if deleted_player:
            # Remove role, restore nickname and clean DB
            if inter.guild.get_role(int(MyRoles.AUTH)) in inter.author.roles:
                await inter.author.remove_roles(inter.guild.get_role(int(MyRoles.AUTH)))
            if inter.guild.get_role(int(MyRoles.REP)) in inter.author.roles:
                tag = re.search(r"\[.+]", inter.author.display_name).group(0)[1:-1]
                if not await remove_representation(inter.author, inter.guild.get_role(int(MyRoles.REP)), mongo, tag):
                    msg = f"Errore durante l'aggiornamento del clan `{tag}`. Controllare il terminale e/o log."
                    await inter.channel.send(msg)
                    mongo.insert_player(
                        deleted_player["discord"],
                        deleted_player["wows"],
                        deleted_player["token"],
                        deleted_player["expire"]
                    )
            msg = f"Logout effettuato con successo. Arrivederci <@{inter.author.id}>"
            try:
                await inter.author.edit(nick=None)
            except errors.Forbidden:
                msg = f"{msg}\n*Avviso* `logout(inter, mongo)`"
                msg = f"{msg}\nPermessi negati durante la modifica dell'utente <@{inter.author.id}>."
            await inter.send(msg)
        else:
            msg = f"Logout dell'utente <@{inter.author.id}> non effettuato."
            msg = f"{msg}\n**Errore** `logout(inter, mongo)`"
            msg = f"{msg}\nUtente <@{inter.author.id}> non è stato trovato e/o cancellato."
            await inter.send(msg)


async def remove_representation(user: Member, role: Role, mongo: "ApiMongoDB", old_clan_tag: str) -> dict:
    await user.author.remove_roles(role)
    clan_data = mongo.get_clan_by_tag(old_clan_tag)
    representations = clan_data["representations"]
    representations.remove(str(user.id))
    return mongo.update_clan_by_id(clan_data["id"], {"representations": representations})
