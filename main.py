import discord
from discord import Intents
from discord.ext import commands,tasks
from discord.utils import get
from discord.errors import DiscordException
import os,sqlite3
from pytube import Channel,streams
import json
import urllib.request
token='' 
msg_id = None
intents = Intents.all()
intents.typing = False
intents.presences = False
client = discord.Client(intents=intents)
client = commands.Bot(command_prefix='p.',intents=intents)
client.remove_command("help")
conn = sqlite3.connect('yt_git.db')
c = conn.cursor()
@tasks.loop(minutes=5)
async def powiadomienie():
    c.execute("SELECT * FROM Channel")
    t=c.fetchall()
    for t in t:
        channel = Channel(f'{t[1]}')
        zm_link=t[1]
        latest_video = channel.videos
        for video in latest_video:
            link=video.watch_url
            id_film=video.video_id
            print(video.title)
            key_api="" #ukryj
            data_f=urllib.request.urlopen("https://www.googleapis.com/youtube/v3/videos?part=statistics&id="+id_film+"&part=snippet&key="+key_api).read()
            publikacja=json.loads(data_f)["items"][0]["snippet"]["publishedAt"] #publikacja filmu/live
            data=publikacja[0:10]
            godzina=publikacja[11:19] #czas jest podany w stefir czasowej UTC+0
            if data>t[2]:
                c.execute("UPDATE Channel SET data_p=? WHERE link=?",(data,zm_link))
                c.execute("UPDATE Channel SET godzina=? WHERE link=?",(godzina,zm_link))
                conn.commit()
                channel = client.get_channel(t[4])
                await channel.send(f"{t[0]} wstawił nowy film.\n  {link}")
            if data==t[2] and godzina>t[3]:
                c.execute("UPDATE Channel SET data_p=? WHERE link=?",(data,zm_link))
                c.execute("UPDATE Channel SET godzina=? WHERE link=?",(godzina,zm_link))
                conn.commit()
                channel = client.get_channel(t[4])
                await channel.send(f"{t[0]} wstawił nowy film.\n  {link}")

            break
    print("_____-----_____-----_____-----_____-----_____-----_____-----")
@client.event
async def on_ready():
    print("Zalogowaliśmy się jako {0.user}".format(client))
    powiadomienie.start()
@client.command()
async def wstaw(ctx,link):
    id_channel = ctx.channel.id
    ch=client.get_channel(id_channel)
    channel = Channel(f'{link}')
    latest_video = channel.videos
    for video in latest_video:
        id_film=video.video_id
        name=video.author
        key_api="" #ukryj
        data_f=urllib.request.urlopen("https://www.googleapis.com/youtube/v3/videos?part=statistics&id="+id_film+"&part=snippet&key="+key_api).read()
        publikacja=json.loads(data_f)["items"][0]["snippet"]["publishedAt"] #publikacja filmu/live
        data=publikacja[0:10]
        godzina=publikacja[11:19]
        c.execute("SELECT * FROM Channel WHERE  link=?",(link,) )
        te=c.fetchall()
        if te:
            await ch.send("Taki kanał jest w bazie danych")
        else:
            c.execute('INSERT INTO Channel VALUES(?,?,?,?,?)',(name,link,data,godzina,id_channel))
            conn.commit()
            await ch.send("Kanał dodany")
        break
def main():
    client.run(token)
if __name__ == '__main__':
    main()
