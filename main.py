import discord
import requests
import json
import riotwatcher
from time import sleep


f = open("keys.json")
keys = json.load(f)
DISCORD_TOKEN = keys["token"]
# Regenerate the lol api key (24hr)
LOL_API_KEY = keys["LOL_API"]


intents = discord.Intents.default()
intents.members = True
intents.message_content = True

client = discord.Client(intents=intents)


class summonerdata:
    def __init__(
        self, name, icon, level, rank, win, lose, winrate, topchamps, livegame
    ) -> None:
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
        playerName, playerRegion = get_name_region(message.content)
        summoner = get_profile_data(playerName, playerRegion)

        botMessage = createEmbed(summoner)

        await message.channel.send(f"{message.author.mention} here it is!")
        await message.channel.send(embed=botMessage)


def get_champname(ChampIdList):
    resp = requests.get(
        "http://ddragon.leagueoflegends.com/cdn/12.6.1/data/en_US/champion.json"
    )
    Data = resp.json()


def get_name_region(message: str) -> tuple[str, str]:
    split = message.split(" ")
    playerName = " ".join(split[2:])
    region = split[1]
    return playerName, region


def get_api_data(Link: str) -> dict:
    print("Getting data...")
    while 1:
        resp = requests.get(Link)
        if resp.status_code == 200 or resp.status_code == 404:
            break
        print(f"Error {resp.status_code} happened. Sleeping for 10 sec...")
        sleep(10)

    Data = resp.json()
    return Data


def get_live_data(Link: str) -> tuple[bool, dict]:

    resp = requests.get(Link)

    return resp.status_code == 200, resp.json()


def get_profile_data(playerName: str, region: str) -> summonerdata:

    # Make request for all necessary data

    API_URL = f"https://{region}1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{playerName}?api_key={LOL_API_KEY}"
    Data = get_api_data(API_URL)

    summonerId = Data["id"]

    CHAMP_API = f"https://{region}1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{summonerId}/top?count=3&api_key={LOL_API_KEY}"
    ChampsData = get_api_data(CHAMP_API)

    RANKED_API = f"https://{region}1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summonerId}?api_key={LOL_API_KEY}"
    RankedData = get_api_data(RANKED_API)

    LIVE_GAME_API = f"https://{region}1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{summonerId}?api_key={LOL_API_KEY}"
    InGame, LiveData = get_live_data(LIVE_GAME_API)

    ChampStr = ""
    for c in ChampsData:
        # instead of champId, write championName
        ChampStr = (
            ChampStr + str(c["championId"]) + ": " + str(c["championPoints"]) + "\n"
        )

    rank = RankedData[1]["tier"] + " " + RankedData[1]["rank"].upper()
    winrate = (
        int(RankedData[1]["wins"])
        / (int(RankedData[1]["wins"]) + int(RankedData[1]["losses"]))
        * 100
    )

    # if player is in game get necessary data
    if InGame:
        GameLength = str(LiveData["gameLength"]).split(" ")[0]
        for participant in LiveData["participants"]:
            if participant["summonerId"] == summonerId:
                LiveChamp = participant["championId"]
                LiveData = f"Playing {LiveChamp} for {GameLength} minutes."
                break
    else:
        LiveData = "N/A Playing"

    # get macth time, champ name

    summoner = summonerdata(
        playerName,
        Data["profileIconId"],
        Data["summonerLevel"],
        rank,
        RankedData[1]["wins"],
        RankedData[1]["losses"],
        f"{winrate:.0f}",
        ChampStr,
        LiveData,
    )

    return summoner


def createEmbed(player: summonerdata) -> discord.embeds.Embed:

    message = discord.Embed(
        title=f"{player.name}", description="Here are all the stats we found:"
    )
    message.set_thumbnail(
        url=f"https://ddragon.leagueoflegends.com/cdn/12.22.1/img/profileicon/{player.icon}.png"
    )
    message.add_field(name="Level:", value=f"{player.level}")
    message.add_field(
        name="Ranked Stats:",
        value=f"{player.rank.capitalize()}\n{player.win}W {player.lose}L\nWinrate: {player.winrate}%",
        inline=True,
    )
    message.add_field(name="Top Champs:", value=f"{player.topchamps}", inline=False)
    message.add_field(name="Live Game:", value=f"{player.livegame}")

    return message


def get_quote() -> str:
    print("Getting Quote....")
    quoteData = get_api_data("https://zenquotes.io/api/random")
    quote = quoteData[0]["q"] + " -" + quoteData[0]["a"]
    return quote


client.run(DISCORD_TOKEN)
