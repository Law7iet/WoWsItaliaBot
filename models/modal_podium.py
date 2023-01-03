from disnake import TextInputStyle, TextChannel, ModalInteraction, ui, Embed, Attachment


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
        super().__init__(title="Modal", custom_id="modal", components=components)

    async def callback(self, inter: ModalInteraction):
        try:

            # Set color
            match self.position:
                case "Primo": color = 0xFFD700
                case "Secondo": color = 0xC0C0C0
                case "Terzo": color = 0xCD7F32
                case _: color = 0xFFFFFF

            # Set edition
            edition = str(self.edition) if not self.edition == '1' else ''

            # Set description
            if self.position == "Partecipante":
                description = f"{self.tournament} {edition}\n\nGiocatori:\n"
            else:
                description = f"**{self.tournament} {edition} - {self.position} classificato**\n\nGiocatori:\n"
            description = description + inter.text_values["players"] + '\n'

            embed = Embed(
                title=inter.text_values["team"],
                description=description,
                color=color
            )
            embed.set_thumbnail(url=self.image.url)
            embed.set_footer(text='Congratulazioni!')

            await self.channel.send(embed=embed)
            await inter.send("Fatto!")

        except Exception as error:
            await inter.response.send_message("Errore durante la generazione del modal.\n\n" + str(error))
