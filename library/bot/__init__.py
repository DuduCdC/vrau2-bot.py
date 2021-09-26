from asyncio import sleep
from datetime import datetime
from apscheduler.triggers.cron import CronTrigger
from glob import glob

from discord import Intents, Embed, File, DMChannel
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.errors import HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase
from discord.ext.commands import CommandNotFound, Context, BadArgument, MissingRequiredArgument,CommandOnCooldown
from discord.ext.commands import when_mentioned_or, command, has_permissions


from ..db import db

PREFIX='+'
OWNER_IDS=[718078880287686740]
COGS = [path.split('\\')[-1][:-3] for path in glob('./library/cogs/*.py')]
IGNORE_EXCEOTIONS = (CommandNotFound,BadArgument)

def get_prefix(bot, message):
    prefix = db.field("SELECT Prefix FROM Guilds WHERE GuildID = ?", message.guild.id)
    return when_mentioned_or(prefix)(bot, message)

class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self,cog,False)

    def ready_up(self,cog):
        setattr(self,cog,True)
        print(f' {cog} cog está pronto.')

    def all_ready(self):
        return all([getattr(self,cog)for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        self.cogs_ready = Ready()
        self.ready = False
        self.guild = None
        self.scheduler = AsyncIOScheduler()

        db.autosave(self.scheduler)
        super().__init__(
            command_prefix=get_prefix,
            owner_ids=OWNER_IDS,
            intents=Intents.all()
            )

    def setup(self):
        for cog in COGS:
            self.load_extension(f"library.cogs.{cog}")
            print(f" {cog} cog carregado.")

        print("Setup completo.")
    
    def run(self, version):
        self.VERSION = version

        print('Fazendo o setup...')
        self.setup()

        with open("./library/bot/token.0", "r", encoding="utf-8") as tf:
            self.TOKEN = tf.read()

        print('Iniciando o bot...')
        super().run(self.TOKEN, reconnect = True)

    async def process_commands(self, message):
        ctx = await self.get_context(message,cls= Context )

        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)

            else:
                await ctx.send("Não to pronto para receber comandos! Espera ai vagabundo.")

    async def rules_reminder(self):
        await self.stdout.send('Só lembrando vcs parem de fzr merda nessa porra!')

    async def on_connect(self):
        print(' Conectando nessa porra!')

    async def on_disconnect(self):
        print('Caiu a porra toda aqui!')

    async def on_resumed(self):
        print("Voltamo familia!")

    

    async def on_error(self,error,*args,**kwargs):
        if error == "on_command_error":
            await args[0].send('Alguma coisa está errada.')

        await self.stdout.send('Ocorreu algum erro.')
        raise

    async def on_command_error(self,ctx,exc):
        # if any([isinstance(exc,error)for error in IGNORE_EXCEOTIONS]):
        #     pass

        if isinstance(exc, CommandNotFound):
            await ctx.send('O comando não foi encontrado.')

        elif isinstance(exc,BadArgument):
            pass

        elif isinstance(exc,MissingRequiredArgument):
            await ctx.send("Um ou mais argumentos estão faltando.")

        elif isinstance(exc, CommandOnCooldown):
            await ctx.send(f"Esse comando está em cooldown. Tente novamente em {exc.retry_after:,.2f} segundos.")
        
        elif isinstance(exc.original,HTTPException):
            await ctx.send("Incapaz de enviar uma mensagem.")

        elif isinstance(exc.original, Forbidden):
            await ctx.send("Eu não tenho permissão para fazer isso.")

        else:
            raise exc.original

    async def on_ready(self):
        if not self.ready:
            
            self.guild = self.get_guild(688815753482338350)
            self.stdout = self.get_channel(877950565542404176)#Log
            self.scheduler.add_job(self.rules_reminder, CronTrigger(day_of_week=0,hour=12,minute=0,second=0))
            self.scheduler.start()

            

            embed = Embed(title = "O pai tá ON!", description ="O Vrau 2.0 chegou porra!", color =0xFF0000, timestamp=datetime.utcnow())
            fields =[("Name","Value",True),
                    ("Outro field","Esse fica logo ao lado do outro.",True),
                    ("Outro field", "Mas esse tem a sua própria linha.",False)]
            for name,value,inline in fields:
                embed.add_field(name=name,value=value,inline=inline)
            embed.set_author(name="Nome do autor...",icon_url=self.guild.icon_url)
            embed.set_footer(text='Esse é o rodapé.')
            embed.set_thumbnail(url=self.guild.icon_url)
            embed.set_image(url=self.guild.icon_url)

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            #await self.stdout.send(embed=embed)
            #await self.stdout.send(file=File('./vrau2-bot.py/data/images/profile.png')) Manda um arquivo no canal

            self.ready = True
            print('To pronto nessa porra!')

        else:
            print('Tinha caido mas levantei!')


    async def on_message(self, message):
        if not message.author.bot:
            if isinstance(message.channel, DMChannel):
                if len(message.content)<50:
                    await message.channel.send("Sua mensagem deve ter no máximo 50 caracteres.")
                else:
                    member = self.guild.get_member(message.author.id)
                    embed =Embed(title="Modmail", color=member.color, timestamp = datetime.utcnow())

                    embed.set_thumbnail(url= member.avatar_url)

                    fields=[("Membro",f"{member.display_name}",False),
                            ("Mensagem",message.content,False)]

                    for name,value,inline in fields:
                        embed.add_field(name=name,value=value,inline=inline)
                    
                    mod = self.get_cog("Mod")
                    await mod.log_channel.send(embed = embed)
                    await message.channel.send("Mesagem repassada aos moderadores.")
            else:
                await self.process_commands(message)

bot = Bot()