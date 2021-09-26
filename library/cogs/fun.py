from random import choice,randint
from typing import Optional

from aiohttp import request
from discord import Member,Embed
from discord.errors import HTTPException
from discord.ext.commands import Cog, command, BadArgument, cooldown, BucketType

import giphy_client
from giphy_client.rest import ApiException
import random


class Fun(Cog):
    def __init__(self,bot):
        self.bot=bot

    # @command(name="cmd",aliases = ["command", "c"],hidden=True,pass_context=False)
    # async def some_amazing_command(self,ctx):
    #     pass

    @command(name="oi",aliases = ["olá","coe","eai"],brief = """Mensagem de olá!""")
    @cooldown(1, 15, BucketType.user)
    async def say_hello(self,ctx):
        
        await ctx.send(f"{choice(('Olá','Oi','Eai'))} {ctx.author.mention}!")

    @command(name="dado",aliases=["num","d"],brief = """Comando para rolar um dado de N faces, N vezes e somar os resultados. """)
    @cooldown(1, 15, BucketType.user)
    async def roll_dice(self,ctx,die_string:str):
        
        dice, value = (int(term) for term in die_string.split("d"))
        if dice <= 25:
            rolls = [randint(1,value) for i in range(dice)]
            
            await ctx.send("+".join([str(r) for r in rolls]) + f" = {sum(rolls)}")
        else:
            await ctx.send("Você tentou rodar o dado muitas vezes. Coloca um número mais baixo ai desgrama.")



    @command(name= "socar",aliases=["soco"],brief= """Esse comando é usado para dar um soco em alguém.""")
    @cooldown(1, 15, BucketType.user)


    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "por roubar um beijão dele(a)"):
        #await ctx.send(f"{ctx.author.display_name} socou {member.mention} {reason}!")
        api_key="e01Vm7IlAe9hMULJ1uWOlpe51n24aibH"
        api_instance = giphy_client.DefaultApi()

        try:
            q="Punch"

            api_response = api_instance.gifs_search_get(api_key,q, limit=60, rating='g')
            lst = list(api_response.data)
            giff = random.choice(lst)

            embed = Embed(description=(f"{ctx.author.display_name} socou {member.mention} {reason}!"),color=ctx.author.color)

            embed.set_image(url = f'https://media.giphy.com/media/{giff.id}/giphy.gif')
            await ctx.channel.purge(limit=1)
            await ctx.channel.send(embed=embed)

        except ApiException as e:
            print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)

    @slap_member.error
    async def slap_member_eror(self,ctx,exc):
        if isinstance(exc,BadArgument):
            await ctx.send("Tá tentando socar fantasma ? Esse membro não existe maluco.")


    @command(name="giff", aliases=["gif"])
    async def gif(self,ctx,*,q="random"):

        api_key="e01Vm7IlAe9hMULJ1uWOlpe51n24aibH"
        api_instance = giphy_client.DefaultApi()

        try: 

            api_response = api_instance.gifs_search_get(api_key, q, limit=5, rating='g')
            lst = list(api_response.data)
            giff = random.choice(lst)

            emb = Embed(title=q)
            emb.set_image(url = f'https://media.giphy.com/media/{giff.id}/giphy.gif')

            await ctx.channel.send(embed=emb)
        except IndexError:
            await ctx.channel.send("Não temos giff sobre isso.")

        except ApiException as e:
            print("Exception when calling DefaultApi->gifs_search_get: %s\n" % e)





    @command(nome="eco",aliases=["say","msg"],brief = """Comando para o bot repetir sua mensagem.""")
    @cooldown(1, 15, BucketType.guild)
    async def echo_message(self,ctx,*,message):
        
        await ctx.message.delete()
        await ctx.send(message)

    @command(name="fact",aliases= ["fato"],brief = """Comando que mostra um fato aleatório sobre um animal (dog, cat, panda, fox, bird, koala).""")
    @cooldown(1, 60, BucketType.user)
    async def animal_fact(self,ctx,animal:str):
        

        if (animal:= animal.lower()) in ("dog", "cat", "panda", "fox","bird", "koala"):
            fact_url = f"https://some-random-api.ml/animal/{animal}"
            image_url = f"https://some-random-api.ml/img/{'birb' if animal == 'bird' else animal}"

            async with request("GET",image_url,headers={}) as response:
                if response.status == 200:
                    data = await response.json()
                    image_url = data["link"]
                
                else:
                    image_url = None

            async with request("GET",fact_url, headers= {}) as response:
                if response.status ==200:
                    data= await response.json()

                    embed=Embed(title= f"{animal.title()} fact",
                    description=data["fact"],
                    colour=ctx.author.colour)
                    
                    if image_url is not None:
                        embed.set_image(url=image_url)

                    await ctx.send(embed=embed)


                else:
                    await ctx.send(f"Não tem fato nenhum sobre esse animal aqui não.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up('fun')

def setup(bot):
    bot.add_cog(Fun(bot))