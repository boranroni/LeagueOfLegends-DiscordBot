import discord
import requests
import json
import riotwatcher


f = open("keys.json")
keys = json.load(f)
DISCORD_TOKEN = keys["token"]
#Regenerate the lol api key (24hr)
LOL_API_KEY = keys["LOL_API"]


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)

class summonerdata:
  def __init__(self,name,icon,level,rank,win,lose,winrate,topchamps,livegame) -> None:
    self.name = name
    self.icon = icon
    self.level = level
    self.rank = rank
    self.win = win
    self.lose = lose
    self.winrate = winrate
    self.topchamps = topchamps
    self.livegame = livegame
     


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))
    print("----------Friday is back home!-----------")

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("!profile"):
        playerName, playerRegion = get_data(message.content)
        summoner = get_profile_data(playerName,playerRegion)
      
        botMessage = createEmbed(summoner)


        await message.channel.send(embed=botMessage)



def get_data(message):

    split = message.split(" ")
    playerName = " ".join(split[2:])
    region = split[1]



    return playerName, region


def get_profile_data(playerName,region):
  API_URL = f"https://{region}1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{playerName}?api_key={LOL_API_KEY}"

  resp = requests.get(API_URL)
  Data = resp.json()
  summonerId = Data["id"]
  
  
  CHAMP_API = f"https://{region}1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{summonerId}/top?count=3&api_key={LOL_API_KEY}" 
  resp = requests.get(CHAMP_API)
  ChampsData = resp.json()

  Champs = {}
  
  for c in ChampsData:
    Champs[c["championId"]] = c["championPoints"]

  summoner = summonerdata(playerName,Data["profileIconId"],Data["summonerLevel"],"plat 3","32","32","12",Champs,"fuckfect") 

  return summoner






def createEmbed(player):

  message = discord.Embed(title=f"{player.name}", description =  "Here are all the stats we found:")
  message.set_thumbnail(url=f"https://ddragon.leagueoflegends.com/cdn/12.22.1/img/profileicon/{player.icon}.png")
  message.add_field(name="Level:",value=f"{player.level}")
  message.add_field(name="Ranked Stats:",value=f"{player.rank.capitalize()}\n{player.win}W {player.lose}L\nWinrate: {player.winrate}%",inline = True)
  message.add_field(name="Top Champs:",value=f"{player.topchamps}", inline=False)
  message.add_field(name="Live Game:",value=f"{player.livegame} playing")


  return message




def get_quote():
    print("Get Quote")
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]["q"] + " -" + json_data[0]["a"]
    return (quote)



client.run(DISCORD_TOKEN)

"""

await lib.discord.channels["@0.3.2"].messages.create({
  "channel_id": `${context.params.event.channel_id}`,
  "content": "",
  "tts": false,
  "embeds": [
    {
      "type": "rich",
      "title": `Nickname`,
      "description": "",
      "color": 0x44afaf,
      "fields": [
        {
          "name": `Player LVl`,
          "value": "\u200B"
        },
        {
          "name": `Player Rank`,
          "value": "\u200B"
        }
      ],
      "image": {
        "url": `https://ddragon.leagueoflegends.com/cdn/12.22.1/img/profileicon/5518.png`,
        "height": 10,
        "width": 10
      },
      "thumbnail": {
        "url": `https://ddragon.leagueoflegends.com/cdn/12.22.1/img/profileicon/5528.png`,
        "height": 0,
        "width": 0
      },
      "footer": {
        "text": `made by boranroni`
      }
    }
  ]
});

def get_data(message):

    print("Get Data")
    mm = message.split(" ")

    playerName = " ".join(mm[2:])
    region = mm[1]
    playerID = playerData["id"]

    PLAYER_API_LINK = f"https://{region}1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{playerName}?api_key={LOL_API_KEY}"

    playerresponse = requests.get(PLAYER_API_LINK)
    playerData = playerresponse.json()

    RANKED_API_LINK = f"https://{region}1.api.riotgames.com/lol/league/v4/entries/by-summoner/{playerID}?api_key={LOL_API_KEY}"

    rankedresponse = requests.get(RANKED_API_LINK)
    rankedData = rankedresponse.json()


    return playerData, rankedData


def createEmbed(playerData, rankedData):

    print("Create Embed")
    mm = message.split(" ")
    playerName = playerData["name"]
    playerLvl = playerData["summonerLevel"]
    iconId = playerData["profileIconId"]
    #playerId = playerData["id"]

    playerWinrate = 0
    if rankedData:
        jsonzero = rankedData[0]
        playerTier = jsonzero["tier"]+" "
        playerWinrate = int((jsonzero["wins"]/jsonzero["losses"])*100)
    else:
        playerTier = "un-"

    iconLink = f"https://ddragon.leagueoflegends.com/cdn/12.22.1/img/profileicon/{iconId}.png"
    #rankedInfo =

    message = discord.Embed(
    title=f"{playerName}",
    description=f"Player's level is {playerLvl} \n {playerTier}ranked \n Winrate is %{playerWinrate}")



    message.set_thumbnail(url=iconLink)

    return message


"""
