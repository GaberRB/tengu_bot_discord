import asyncio
import os
import youtube_dl as yt
import discord
from requests import get

YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
}
async def search(arg):

    with yt.YoutubeDL(YDL_OPTIONS) as ydl:
        try:
            get(arg)
        except:
            video = ydl.extract_info(f"ytsearch:{arg}", download=False)['entries'][0]
        else:
            video = ydl.extract_info(arg, download=False)
    data = {'url': video['webpage_url'],'title': video['title'] }
    return data

def readToken():
    file = open('token', 'r')
    token = file.read()
    file.close()
    return  token

class Youtube:
    DISCORD_TOKEN = readToken()

    intents = discord.Intents().all()
    client = discord.Client(intents=intents)

    yt.utils.bug_reports_message = lambda: ''

    ffmpeg_options = {
        'options': '-vn'
    }


    ytdl = yt.YoutubeDL(YDL_OPTIONS)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = ""


    @classmethod
    async def from_url(cls, find, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: Youtube.ytdl.extract_info(find, download=not stream))
        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        filename = data['title'] if stream else Youtube.ytdl.prepare_filename(data)
        return filename