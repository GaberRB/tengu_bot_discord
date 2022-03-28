import time

import discord
from discord.ext import commands
import os
import glob
from PIL import Image
import ascii_magic
from src.apis.WikiHowApi.HowToStep import search_wikihow
from src.apis.Youtube import Youtube
from src.apis.Pywhatkit_asciiart import image_to_ascii_art as kt
from src.apis.botSugerePc import MontaPC
import aiohttp
import json
import re
import random
client = commands.Bot(command_prefix="$")

def readToken():
    file = open('token', 'r')
    token = file.read()
    file.close()
    return  token

token =  readToken()


@client.command()
async def comandos(ctx):
    embed = discord.Embed(title="Commands")
    embed.add_field(name="$montapc", value="Monta um pc gamer com links da Kabum", inline=False)
    embed.add_field(name="$drawImg", value="Draw attachment png, jpeg, gif, jpg", inline=False)
    embed.add_field(name="asciiArt", value="Draw Ascii Art Color attachment png, jpeg, gif, jpg", inline=False)
    embed.add_field(name="$chama", value="Speach a message", inline=False)
    embed.add_field(name="$tutorial", value="Search a tutorial by WikiHow", inline=False)
    embed.add_field(name="$join", value="Tells the bot to join the voice channel", inline=False)
    embed.add_field(name="$leave", value="To make the bot leave the voice channel", inline=False)
    embed.add_field(name="$play", value="To play song", inline=False)
    embed.add_field(name="$pause", value="This command pauses the song", inline=False)
    embed.add_field(name="$resume", value="Resumes the song", inline=False)
    embed.add_field(name="$stop", value="Stops the song", inline=False)
    embed.add_field(name="$info", value="Made by GaberRB", inline=False)
    await ctx.send(content=None, embed=embed)

@client.command()
async def info(ctx):
    embed = discord.Embed(
        title='GaberRB',
        url='https://github.com/GaberRB',
        description="please follow my github, i really appreciate it <3",
        color=discord.Colour.dark_teal()
    )
    await ctx.send(embed=embed)

@client.command()
async def chama(ctx, *, args):
    await ctx.send(args, tts=True)

@client.command()
async def tutorial(ctx, *, args):
    max_results = 1
    how_tos = search_wikihow(args, max_results, lang="pt")
    await ctx.send(how_tos[0].print(), tts=True)

@client.command()
async def montapc(ctx):
    user = ctx.message.author
    print('entrei no montapc')
    token = ""
    trending = 'https://api.giphy.com/v1/gifs/search?q='
    gifs = ['computer', 'pcgamer', 'gamer', 'pc']
    precos = 0
    pecas = []
    async with ctx.typing():
        for peca in MontaPC.lerComponentes():
            embed = discord.Embed(
                title=peca['componente'].upper(),
                url=peca['link'],
                description= f"{peca['descricao']} {peca['preco']}",
                color=discord.Colour.dark_teal()
            )
            try:
                preco = re.findall("\d+\.\d+", peca['preco']).pop()
            except IndexError:
                preco = '0'
            precos += float(preco)
            await ctx.send(embed=embed)
        print('buscando gif')
        session = aiohttp.ClientSession()
        response = await session.get(f'{trending}{gifs[random.randrange(len(gifs))]}&api_key={token}&limit=10')
        gif_choice = random.randint(0,3)
        data = json.loads(await response.text())

        embedGif = discord.Embed(
            title=str(f'@{user} seu PCGamer ficou R$ {round(precos, 2)}'),
            colour=discord.Colour.blue(),
        ).set_image(url=data['data'][gif_choice]['images']['original']['url'])
        await session.close()
        await ctx.send(embed=embedGif)

@client.command()
async def drawImg(ctx):
    image_types = ["png", "jpeg", "gif", "jpg"]
    for attachment in ctx.message.attachments:
        if any(attachment.filename.lower().endswith(image) for image in image_types):
            path = attachment.filename
            await attachment.save(path)
            kt.image_to_ascii_art(path, f'{path}')
            await ctx.send(file=discord.File(f'{path}.txt'))
            time.sleep(10)
    files = glob.glob(path)
    for f in files:
        os.remove(f)

@client.command()
async def asciiArt(ctx):
    image_types = ["png", "jpeg", "gif", "jpg"]
    for attachment in ctx.message.attachments:
        if any(attachment.filename.lower().endswith(image) for image in image_types):
            path = attachment.filename
            await attachment.save(path)
            my_art = ascii_magic.from_image_file(
                path,
                columns=200,
                width_ratio=2,
                mode=ascii_magic.Modes.HTML
            )
            ascii_magic.to_html_file(f'{path}.html', my_art)
            await ctx.send(file=discord.File(f'{path}.html'))
            time.sleep(10)
    files = glob.glob(path)
    for f in files:
        os.remove(f)

@client.command()
async def join(ctx):
    channel = ctx.author.voice.channel
    voice = None
    for vc in client.voice_clients:
        if vc.guild == ctx.guild:
            voice = vc
    if not channel:
        await ctx.send("You are not in a vocal channel.")
        return
    if voice and voice.is_connected():
        vc = await voice.move_to(channel)
    elif voice == channel:
        return
    else:
        vc = await channel.connect()
    return vc

@client.command()
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await voice_client.disconect()
    else:
        await ctx.send("The bot is not connected to a voice channel")

@client.command()
async def play(ctx, *, music):
    user = ctx.message.author
    vc = user.voice.channel

    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice == None:
        await join(ctx)
        await ctx.send(f"Joined **{vc}**")
        server = ctx.message.guild
        voice_channel = server.voice_client
        data = await Youtube.search(music)
        embed = discord.Embed(
            title=data['title'],
            url=data['url'],
            description=f"Order: {user} <====Now Playing====> Tengu BOT",
            color=discord.Colour.dark_teal()
        )
        await ctx.send(embed=embed)

        async with ctx.typing():
            filename = await Youtube.YTDLSource.from_url(find=data['url'], loop=client.loop)
            voice_channel.play(discord.FFmpegPCMAudio(filename))
    else:
        server = ctx.message.guild
        voice_channel = server.voice_client
        data = await Youtube.search(music)
        embed = discord.Embed(
            title=data['title'],
            url=data['url'],
            description=f"Order: {user} <====Now Playing====> Tengu BOT",
            color=discord.Colour.dark_teal()
        )
        await ctx.send(embed=embed)

        async with ctx.typing():
            filename = await Youtube.YTDLSource.from_url(find=data['url'], loop=client.loop)
            voice_channel.play(discord.FFmpegPCMAudio(filename))

@client.command()
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")

@client.command()
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this. Use play_song command")

@client.command()
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.stop()
    else:
        ctx.send("The bot is not playing anything at the moment.")

client.run(token)