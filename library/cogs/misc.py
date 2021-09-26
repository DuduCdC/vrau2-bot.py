from discord.ext.commands import Cog
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions

from ..db import db

class Misc(Cog):
	def __init__(self, bot):
		self.bot = bot

	@command(name="prefixo",brief= """Comando para definir um novo prefixo para o servidor.""")
	@has_permissions(manage_guild=True)
	async def change_prefix(self, ctx, new: str):
		if len(new) > 5:
			await ctx.send("O bot só pode ter 5 prefixos.")

		else:
			db.execute("UPDATE guilds SET Prefix = ? WHERE GuildID = ?", new, ctx.guild.id)
			await ctx.send(f"O prefixo selecionado foi {new}.")

	@change_prefix.error
	async def change_prefix_error(self, ctx, exc):
		if isinstance(exc, CheckFailure):
			await ctx.send("Você precisa da permissão de gerenciador o servidor para fazer isso.")

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("misc")

def setup(bot):
	bot.add_cog(Misc(bot))