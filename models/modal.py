from disnake import TextInputStyle, Role, TextChannel, ModalInteraction, ui, Embed


class Modal(ui.Modal):
    def __init__(self, role: Role | None, channel: TextChannel, message: str = None):
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
        super().__init__(title="Modal", custom_id="modal", components=components)

    async def callback(self, inter: ModalInteraction):
        try:
            if self.message_id is None:
                embed = Embed(
                    title=inter.text_values["title"],
                    description=inter.text_values["description"],
                    color=0xffffff
                )
                if self.role:
                    await self.channel.send("<@" + str(self.role.id) + ">", embed=embed)
                else:
                    await self.channel.send(embed=embed)
            else:
                message = await self.channel.fetch_message(int(self.message_id))
                old_embed = message.embeds[0]
                if inter.text_values["description"] == "":
                    new_description = old_embed.description
                else:
                    new_description = inter.text_values["description"]
                embed = Embed(
                    title=old_embed.title if inter.text_values["title"] == "" else inter.text_values["title"],
                    description=new_description,
                    color=0xffffff
                )
                if self.role:
                    await message.edit(content="<@" + str(self.role.id) + ">", embed=embed)
                else:
                    await message.edit(content="", embed=embed)
            await inter.send("Fatto!")
        except AttributeError:
            await inter.send("Messaggio non trovato.")
        except ValueError:
            await inter.send("ID del messaggio non corretto.")
        except Exception as error:
            await inter.response.send_message("Errore durante la generazione del modal.\n" + str(error))
