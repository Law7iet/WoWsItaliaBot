from disnake import TextInputStyle, Role, TextChannel, ModalInteraction, ui, Embed, Attachment

from utils.functions import send_response_and_clear


class Modal(ui.Modal):
    def __init__(self, role: Role, channel: TextChannel, message: str = None):
        self.role = role
        self.channel = channel
        self.message_id = message
        components = [
            ui.TextInput(
                label="Titolo",
                placeholder="Inserisci qua il titolo.",
                custom_id="title",
                style=TextInputStyle.short,
                required=False
            ),
            ui.TextInput(
                label="Testo",
                placeholder="Inserisci qua il messaggio.",
                custom_id="description",
                style=TextInputStyle.paragraph,
                required=not self.message_id
            )
        ]
        super().__init__(
            title="Modal",
            custom_id="modal",
            components=components
        )

    async def callback(self, inter: ModalInteraction):
        try:
            if self.message_id is None:
                embed = Embed(
                    title=inter.text_values["title"],
                    description=inter.text_values["description"],
                    color=0xffffff
                )
                await self.channel.send("<@&" + str(self.role.id) + ">", embed=embed)
            else:
                message = await self.channel.fetch_message(int(self.message_id))
                old_embed = message.embeds[0]
                embed = Embed(
                    title=old_embed.title if inter.text_values["title"] == "" else inter.text_values["title"],
                    description=old_embed.description if inter.text_values["description"] == "" else inter.text_values["description"],
                    color=0xffffff
                )
                await message.edit(content="<@&" + str(self.role.id) + ">", embed=embed)
            await send_response_and_clear(inter, False, "Fatto!")

        except AttributeError:
            await send_response_and_clear(inter, False, "Messaggio non trovato.")
        except ValueError:
            await send_response_and_clear(inter, False, "ID del messaggio non corretto.")
        except Exception as error:
            await inter.response.send_message("Errore durante la generazione del modal.\n" + str(error))


class ModalPodium(ui.Modal):
    def __init__(self, channel: TextChannel, tournament: str, edition: int, position: str, image: Attachment):
        self.channel = channel
        self.tournament = tournament
        self.edition = edition
        self.position = position
        self.image = image
        components = [
            ui.TextInput(
                label="Clan o Team",
                placeholder="Inserisci qua il nome del clan o del team.",
                custom_id="team",
                style=TextInputStyle.short,
                required=True
            ),
            ui.TextInput(
                label="Giocatori (uno per ogni riga):",
                placeholder="Inserisci qua il giocatori del clan o del team.",
                custom_id="players",
                style=TextInputStyle.paragraph,
                required=True
            )
        ]
        super().__init__(
            title="Modal",
            custom_id="modal",
            components=components
        )

    async def callback(self, inter: ModalInteraction):
        try:

            # Set color
            match self.position:
                case "Primo":
                    color = 0xFFD700
                case "Secondo":
                    color = 0xC0C0C0
                case "Terzo":
                    color = 0xCD7F32
                case _:
                    color = 0xFFFFFF

            # Set edition
            edition = str(self.edition) if not self.edition == '1' else ''

            # Set description
            if self.position == "Partecipante":
                descrizione = self.tournament + ' ' + edition + '\n\nGiocatori:\n'
            else:
                descrizione = '**' + self.tournament + ' ' + edition + ' - ' + self.position + ' classificato**\n\nGiocatori:\n'
            descrizione = descrizione + inter.text_values["players"] + '\n'

            embed = Embed(
                title=inter.text_values["team"],
                description=descrizione,
                color=color
            )
            embed.set_thumbnail(url=self.image.url)
            embed.set_footer(text='Congratulazioni!')

            await self.channel.send(embed=embed)
            await send_response_and_clear(inter, False, "Fatto!")

        except Exception as error:
            await inter.response.send_message("Errore durante la generazione del modal.\n\n" + str(error))
