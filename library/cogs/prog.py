from discord.ext.commands import Cog
from discord.ext.commands import command

class Prog(Cog):
    def __init__(self,bot):
        self.bot = bot
    
    @command(name="prog",aliases = ["p"],brief = """Comando para mando um código de programação dentro do limite de caracteres do discord""")
    async def prog(self,ctx,*,msg):
        
        await ctx.channel.purge(limit=1)
        await ctx.send(f"`{msg}`")



    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("prog")


def setup(bot):
    bot.add_cog(Prog(bot))