
from asyncio import sleep
from datetime import datetime, timedelta
from typing import Optional
from re import search

from discord.ext.commands import Cog, Greedy
from discord.ext.commands import CheckFailure
from discord.ext.commands import command, has_permissions, bot_has_permissions

from better_profanity import profanity
from discord import Embed, Member
from discord.message import Attachment
from discord.utils import _URL_REGEX

from ..db import db

profanity.load_censor_words_from_file("./data/profanity.txt")
class Mod(Cog):
    def __init__(self,bot):
        self.bot = bot

        self.url_regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
        self.links = (878957694042636309,857567532474957835,784987071831998484,866140463295365120,878962095406874644,890349401409724446)
        self.images = (696913398100656162,778867553061437494,878379640203399198,880542054952894528,877563532651139122,890349401409724446)


    @command(name="kick",brief= """Comando para expulsar um membro do servidor.""")
    @bot_has_permissions(kick_members = True)
    @has_permissions(kick_members = True)
    async def kick_members(self, ctx, targets: Greedy[Member],*, reason: Optional[str] = "Sem motivo."):
        if not len(targets):
            await ctx.send("Um ou mais argumentos estão faltando.")
        else:
            for target in targets:
                if (ctx.guild.me.top_role.position > target.top_tole.position and not target.guild_permissions.adminnistrator):
                    await target.kick(reason=reason)

                    embed =Embed(title="Membro Expulso", color=0xFF0000, timestamp = datetime.utcnow())

                    embed.set_thumbnail(url= target.avatar_url)

                    fields=[("Member",f"{target.display_name} ou {target.name}",False),
                            ("Expulso por",ctx.author.display_name,False),
                            ("Motivo",reason,False)]

                    for name,value,inline in fields:
                        embed.add_field(name=name,value=value,inline=inline)
                    

                    await self.log_channel.send(embed = embed)
                else:
                    await ctx.send(f"{target.display_name} não pode ser expulso.")
            await ctx.send("Membro expulso.")


    @kick_members.error
    async def kick_members_eroor(self,ctx,exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Sem permisão para realizar a ação.")

    
    @command(name="ban",brief= """Comando para banir um mebro do servidor.""")
    @bot_has_permissions(ban_members = True)
    @has_permissions(ban_members = True)
    async def ban_members(self, ctx, targets: Greedy[Member],*, reason: Optional[str] = "Sem motivo."):
        if not len(targets):
            await ctx.send("Um ou mais argumentos estão faltando.")
        else:
            for target in targets:
                if (ctx.guild.me.top_role.position > target.top_tole.position and not target.guild_permissions.adminnistrator):
                    await target.ban(reason=reason)

                    embed =Embed(title="Membro Banido", color=0xFF0000, timestamp = datetime.utcnow())

                    embed.set_thumbnail(url= target.avatar_url)

                    fields=[("Membro",f"{target.display_name} também conhecido como {target.name}",False),
                            ("Banido por",ctx.author.display_name,False),
                            ("Motivo",reason,False)]

                    for name,value,inline in fields:
                        embed.add_field(name=name,value=value,inline=inline)
                    

                    await self.log_channel.send(embed = embed)
                else:
                    await ctx.send(f"{target.display_name} não pode ser banido.")
            await ctx.send("Membro banido.")

    @ban_members.error
    async def ban_members_eroor(self,ctx,exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Sem permisão para realizar a ação.")

    @command(name="clear",aliases=["purge"],brief= """Comando para apagar mensagens do canal.""")
    @bot_has_permissions(manage_messages=True)
    @has_permissions(manage_messages=True)
    async def clear_message(self,ctx,targets: Greedy[Member], limit: Optional[int] = 1):
        def _check(message):
            return not len(targets) or message.author in targets

        if 0 < limit <= 100:
            with ctx.channel.typing():
                await ctx.message.delete()
                deleted = await ctx.channel.purge(limit=limit,after = datetime.utcnow()- timedelta(days=14),check = _check)

                await ctx.send(f"{len(deleted):,} mensagens foram apagadas.",delete_after = 5)
        else:
            await ctx.send("Esse limite aí não dá passa um de 1 a 100!")


    @command(name="mute")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles = True)
    async def mute_members(self,ctx,targets: Greedy[Member], hours: Optional[int] = 1 ,*, reason: Optional[str] = "Sem motivo."):
        if 1<= hours < 120:
            if not len(targets):
                await ctx.send("Um ou mais argumentos estão faltando.")
            else:
                unmutes = []

                for target in targets:
                    if not self.mute_role in target.roles:
                        if ctx.guild.me.top_role.position > target.top_role.position:
                            roles_ids = ",".join([str(r.id) for r in target.roles])
                            ent_time = datetime.utcnow() + timedelta(seconds=hours) if hours else None

                            db.execute("INSERT INTO mutes VALUES(?,?,?)", target.id,roles_ids,getattr(ent_time,"isoformat", lambda: None )())

                            await target.edit(roles=[self.mute_role])

                            embed =Embed(title="Membro Mutado", color=0xDD2222, timestamp = datetime.utcnow())

                            embed.set_thumbnail(url= target.avatar_url)

                            fields=[("Member",f"{target.display_name} também conhecido como {target.name}",False),
                                ("Mutado por",ctx.author.display_name,False),
                                ("Duração",f"{hours:,} hora(s)" if hours else "Indefinida",False),
                                ("Motivo",reason,False)]

                            for name,value,inline in fields:
                                embed.add_field(name=name,value=value,inline=inline)

                            await self.log_channel.send(embed = embed)

                            if hours:
                                unmutes.append(target)
                        else:
                            await ctx.send(f"{target.display_name} não pode ser mutado.")

                    else:
                        await ctx.send(f"{target.display_name} já está mutado")   
                await ctx.send("Membro Mutado.")

                if len(unmutes):
                    await sleep(hours)
                    await self.unmute(ctx,targets)
        else:
            await ctx.send("Colocou tempo demais ai mamaco!")
        
    @mute_members.error
    async def mute_members_eroor(self,ctx,exc):
        if isinstance(exc, CheckFailure):
            await ctx.send("Sem permisão para realizar a ação.")

    async def unmute(self,ctx,targets,reason="Acabou o tempo do mute."):

        for target in targets:
            if self.mute_role in target.roles:
                role_ids = db.field("SELECT RoleIDs FROM mutes WHERE UserID = ?",target.id)
                roles=[ctx.guild.get_role(int(id_)) for id_ in role_ids.split(",") if len(id_)]

                db.execute("DELETE FROM mutes WHERE UserID = ?", target.id)
                await target.edit(roles=roles)

                embed =Embed(title="Membro Desmutado", color=0xDD2222, timestamp = datetime.utcnow())

                embed.set_thumbnail(url= target.avatar_url)

                fields=[("Member",target.display_name,False),
                            ("Motivo",reason,False)]

                for name,value,inline in fields:
                    embed.add_field(name=name,value=value,inline=inline)
                    

                await self.log_channel.send(embed = embed)

    @command(name="unmute")
    @bot_has_permissions(manage_roles=True)
    @has_permissions(manage_roles = True)
    async def unmute_members(self,ctx,targets: Greedy[Member],*, reason: Optional[str] = "Sem motivo."):
        if not len(targets):
            await ctx.send("Um ou mais argumentos estão faltando.")
        else:
            await self.unmute(ctx,targets,reason=reason)


    @command(name = "addbanword",aliases = ["addword"])
    @has_permissions(manage_guild=True)
    async def add_profanity(self,ctx,*words):
        with open("./data/profanity.txt","a", encoding="utf-8") as f:
            f.write("".join([f"{w}\n" for w in words]))

            profanity.load_censor_words_from_file("./data/profanity.txt")

            await ctx.send("Palavra adicionada.")

    @command(name = "delbanword",aliases = ["removeword"])
    @has_permissions(manage_guild=True)
    async def remove_profanity(self,ctx,*words):
        with open("./data/profanity.txt","r", encoding="utf-8") as f:
            stored = [w.strip() for w in f.readlines()]

        with open("./data/profanity.txt","w", encoding="utf-8") as f:
            f.write("".join([f"{w}\n" for w in stored if w not in words]))

        profanity.load_censor_words_from_file("./data/profanity.txt")
        await ctx.send("Palavra removida.")

        
        

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:

            self.log_channel = self.bot.get_channel(866088754408980481)
            self.mute_role = self.bot.guild.get_role(877937593558380596)

            unmutes = []
            active_mutes = db.records("SELECT UserID,EndTime FROm mutes")

            for userid,endtime in active_mutes:
                if endtime and datetime.utcnow() > (et := datetime.fromisoformat(endtime)):
                    unmutes.append(self.bot.guild.get_member(userid))

                else:
                    self.bot.scheduler.add_job(self.unmute,"date",run_date = et,args=[self.bot.guild,[self.bot.guild.get_member(userid)]])
            if len(unmutes):
                await self.unmute(self.bot.guild,unmutes)
 
            self.bot.cogs_ready.ready_up("mod")

    @Cog.listener()
    async def on_message(self,message):
        if not message.author.bot:
            if profanity.contains_profanity(message.content):
                await message.delete()
                await message.channel.send ("Você não pode mandar uma menssagem com essa palavra aqui.",delete_after = 10)


            elif message.channel.id not in self.links and search(self.url_regex,message.content):
                await message.delete()
                await message.channel.send("Você não pode mandar links nesse canal.",delete_after = 10)


            if (message.channel.id not in self.images and any([hasattr(a,"width")for a in message.attachments])):
                await message.delete()
                await message.channel.send("Você não pode mandar imagens nessa canal.",delete_after = 10)


def setup(bot):
    bot.add_cog(Mod(bot))