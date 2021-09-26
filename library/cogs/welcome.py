from discord import Forbidden, Embed
from discord.ext.commands import Cog
from discord.ext.commands import command
from datetime import datetime

from ..db import db

class Welcome(Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("welcome")

    @Cog.listener()
    async def on_member_join(self,member):
        guild=self.bot.guild
        channel = self.bot.get_channel(851188095487180820)
        db.execute("INSERT INTO exp (UserID) VALUES (?)", member.id)

        bemvindo= Embed(title="Olá! Bem-vindo(a)!", color =0x0000FF, description=f"{member.mention} seja bem-vindo(a) ao {guild.name}! Faça amigos e divirta-se!", timestamp = datetime.utcnow())
        bemvindo.add_field(name = "ID",value = member.id)
        bemvindo.add_field(name= "Quantidade de membros no servidor", value=len(guild.members))
        bemvindo.set_author(name=member.name,icon_url=member.avatar_url)
        bemvindo.set_thumbnail(url= member.avatar_url)
   
        await channel.send(embed=bemvindo)

        #Se quiser mandar DM quando alguem entra no server.
        # try:
        #     await member.send(f"Bem-vindo ao **{member.guild.name}** {member.mention}!")
        # except Forbidden:
        #     pass

        await member.add_roles(member.guild.get_role(851184247679090689))

        #await member.edit(roles= [*member.roles, *[member.guild.get_role(id_) for id_ in (851184247679090689)]])
    
    @Cog.listener()
    async def on_member_remove(self,member):

        guild=self.bot.guild
        channel = self.bot.get_channel(851187599955066921)
        db.execute("DELETE FROM exp WHERE UserID= ?", member.id)

        tchau = Embed(title="Saiu do Servidor !", color =0x0000FF, description=f"{member.mention} chutou o balde saiu do {guild.name}!", timestamp = datetime.utcnow())
        tchau.add_field(name = "ID",value = member.id)
        tchau.add_field(name= "Quantidade de membros no servidor", value=len(guild.members))
        tchau.set_author(name=member.name,icon_url=member.avatar_url)
        tchau.set_thumbnail(url= member.avatar_url)
        
        await channel.send(embed=tchau)

def setup(bot):
    bot.add_cog(Welcome(bot))