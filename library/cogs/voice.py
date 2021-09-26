from discord.channel import CategoryChannel
from discord.ext.commands import Cog,command
from discord.ext.tasks import loop

from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import discord
from ..db import db

class Voice(Cog):
    def __init__(self,bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.guild = self.bot.get_guild(688815753482338350)

    
    @command(name="voice")
    async def voice(self,ctx,categoria,canal):
        try:
            db.execute("INSERT INTO voice (GuildID) VALUES (?)",ctx.guild.id)
        except:
            return 
        db.execute("UPDATE voice SET Verify = ? WHERE GuildID = ?", 1, ctx.guild.id)
        db.execute("UPDATE voice SET Category = ? WHERE GuildID = ?",categoria, ctx.guild.id)
        db.execute("UPDATE voice SET Channel = ? WHERE GuildID = ?", canal, ctx.guild.id)
        db.commit()
        return (categoria,canal)

    async def cria_canais(self):
        guild=self.guild
        try:
            verificador = db.field("SELECT Verify FROM voice WHERE GuildID = ?",guild.id)
            if int(verificador) == 1:
                    categoria_escolhida_nome = db.field("SELECT Category FROM voice WHERE GuildID = ?",guild.id)
                    categoria = discord.utils.get(guild.categories, name=categoria_escolhida_nome)
                    canal_principal_nome = db.field("SELECT Channel FROM voice WHERE GuildID = ?",guild.id)
                    canal_principal = discord.utils.get(guild.voice_channels, name= canal_principal_nome)

                    canais_da_categoria = categoria.channels
                    id_dos_canais = []
                    membro_canal_principal = canal_principal.members
                    id_dos_usuários = []

            #Criando uma lista com o ID de todos os usuários no canal

                    for membro in membro_canal_principal: 
                        id_dos_usuários.append(membro.id)

            #Criando uma lista com o ID de todos os canais na categoria

                    for canais in canais_da_categoria:
                        id_dos_canais.append(canais.id)
                        nome = canal_principal_nome #NOME DOS CANAIS QUE SERAM CRIADOS

            #Verificando se o primeiro canal já foi criado
                    if len(id_dos_canais)>=2:
                        primeiro_canal_criado = True
                    else:
                        primeiro_canal_criado = False

            #Parte de criação dos canais
                    if primeiro_canal_criado == False:
                        if id_dos_usuários != []:
                            await guild.create_voice_channel(nome, category=categoria)
                            primeiro_canal_criado = True
                            return

                    ultimo_canal = discord.utils.get(guild.voice_channels, id=id_dos_canais[-1])
                    membros_ultimo_canal = ultimo_canal.members

                    if  len(membros_ultimo_canal) >= 1:
                        await guild.create_voice_channel(nome, category=categoria)
                        return

            #Parte de deletar os canais

                #     if len(id_dos_canais)> 1:
                #         penultimo_canal = discord.utils.get(guild.voice_channels, id=id_dos_canais[-2])
                #         membros_penultimo_canal = penultimo_canal.members

                #         if membros_ultimo_canal == [] and membros_penultimo_canal == []:
                #             await ultimo_canal.delete()
                # # Parte de deletar o primeiro canal se tiver vazio

                #         primeiro_canal = discord.utils.get(guild.voice_channels, id=id_dos_canais[0])
                #         membros_primeiro_canal = primeiro_canal.members

                #         if membros_primeiro_canal == []:
                #             await primeiro_canal.delete()

                    for canal in canais_da_categoria:
                        ultimo = len(canais_da_categoria) - 1
                        ultimo_canal_id = canais_da_categoria[ultimo].id
                        canal_membros = canal.members
                        if len(id_dos_canais)> 1 and canal.id != ultimo_canal_id and canal_membros == []:
                            await canal.delete()
        except:
            return




    @Cog.listener()
    async def on_ready(self):

        seconds_list = list(range(60))
        seconds=str(seconds_list)[1:-1]

        self.guild = self.bot.get_guild(688815753482338350)
        self.stdout = self.bot.get_channel(877950565542404176)
        self.scheduler.add_job(self.cria_canais, CronTrigger(second=seconds))
        if self.scheduler.start() is False:
            self.scheduler.start()


        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("voice")


def setup(bot):
    bot.add_cog(Voice(bot))