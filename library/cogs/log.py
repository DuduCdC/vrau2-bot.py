from datetime import datetime

from discord import Embed
from discord.ext.commands import Cog
from discord.ext.commands import command


class Log(Cog):
	def __init__(self, bot):
		self.bot = bot

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.log_channel = self.bot.get_channel(866088754408980481)
			self.bot.cogs_ready.ready_up("log")

	@Cog.listener()
	async def on_user_update(self, before, after):
		if before.name != after.name:
			embed = Embed(title="Troca de Nome de usuário",
						  colour=after.colour,
						  timestamp=datetime.utcnow())

			fields = [("Antes", before.name, False),
					  ("Depois", after.name, False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)

			await self.log_channel.send(embed=embed)

		if before.discriminator != after.discriminator:
			embed = Embed(title="Troca de tag",
						  colour=after.colour,
						  timestamp=datetime.utcnow())

			fields = [("Antes", before.discriminator, False),
					  ("Depois", after.discriminator, False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)

			await self.log_channel.send(embed=embed)

		if before.avatar_url != after.avatar_url:
			embed = Embed(title="Troca de icone",
						  description=f"{self.log_channel.guild.get_member(after.id).mention} Trocou de icone. O novo icone está abaixo. O antigo ao lado.",
						  colour=self.log_channel.guild.get_member(after.id).colour,
						  timestamp=datetime.utcnow())

			embed.set_thumbnail(url=before.avatar_url)
			embed.set_image(url=after.avatar_url)

			await self.log_channel.send(embed=embed)

	@Cog.listener()
	async def on_member_update(self, before, after):
		if before.display_name != after.display_name:
			embed = Embed(title="Troca de Apelido",
						  colour=after.colour,
						  timestamp=datetime.utcnow())

			fields = [("Antes", before.display_name, False),
					  ("Depois", after.display_name, False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)

			await self.log_channel.send(embed=embed)

		elif before.roles != after.roles:
			embed = Embed(title="Atualização de cargos",
						  colour=after.colour,
						  timestamp=datetime.utcnow())

			fields = [("Antes", ", ".join([r.mention for r in before.roles]), False),
					  ("Depois", ", ".join([r.mention for r in after.roles]), False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)
			embed.add_field(name="Membro",value =after.display_name,inline=False)
			await self.log_channel.send(embed=embed)

	@Cog.listener()
	async def on_message_edit(self, before, after):
		if not after.author.bot and not str(after.author) == "Dudu#7034":
			if before.content != after.content:
				embed = Embed(title="Mensagem editada:",
							  description=f"Editada por {after.author.display_name}.",
							  colour=after.author.colour,
							  timestamp=datetime.utcnow())

				fields = [("Antes", before.content, False),
						  ("Depois", after.content, False)]

				for name, value, inline in fields:
					embed.add_field(name=name, value=value, inline=inline)

				await self.log_channel.send(embed=embed)

	@Cog.listener()
	async def on_message_delete(self, message):
		if not message.author.bot and not str(message.author) == "Dudu#7034":
			embed = Embed(title="Mesagem deletada",
						  description=f"Deletada por {message.author.display_name}.",
						  colour=message.author.colour,
						  timestamp=datetime.utcnow())

			fields = [("Conteúdo", message.content, False)]

			for name, value, inline in fields:
				embed.add_field(name=name, value=value, inline=inline)

			await self.log_channel.send(embed=embed)


def setup(bot):
	bot.add_cog(Log(bot))