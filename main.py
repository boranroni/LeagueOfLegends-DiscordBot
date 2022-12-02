import discord
from requests import get
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


class Summoner:
    def __init__(
        self,
        name,
        icon,
        level,
        rank,
        league_point,
        win,
        lose,
        winrate,
        topchamps,
        livegame,
    ) -> None:
        self.name = name
        self.icon = icon
        self.level = level
        self.rank = rank
        self.league_point = league_point
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
        player_name, playerRegion = get_name_region(message.content)
        summoner = get_profile_data(player_name, playerRegion)

        botMessage = createEmbed(summoner)

        await message.channel.send(f"{message.author.mention} here it is!")
        await message.channel.send(embed=botMessage)


def get_champname(ChampId: str) -> str:
    # print("looking for", ChampId)
    resp = get(
        "http://ddragon.leagueoflegends.com/cdn/12.22.1/data/en_US/champion.json"
    )
    Data = resp.json()
    for champ in Data["data"].values():
        if champ["key"] == ChampId:
            # print("found", champ["id"])
            return champ["id"]
    return ""


def get_name_region(message: str) -> tuple[str, str]:
    split = message.split(" ")
    player_name = " ".join(split[2:])
    region = split[1]
    return player_name, region


def get_api_data(Link: str) -> dict:
    print("Getting data...")
    while True:
        resp = get(Link)
        if resp.status_code == 200 or resp.status_code == 404:
            break
        print(f"Error {resp.status_code} happened. Sleeping for 10 sec...")
        sleep(10)

    Data = resp.json()
    return Data


def get_live_data(Link: str) -> tuple[bool, dict]:

    resp = get(Link)

    return resp.status_code == 200, resp.json()


def get_profile_data(player_name: str, region: str) -> Summoner:

    # Make request for all necessary data

    API_URL = f"https://{region}1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{player_name}?api_key={LOL_API_KEY}"
    summoner_data = get_api_data(API_URL)

    summoner_id = summoner_data["id"]

    CHAMP_API = f"https://{region}1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{summoner_id}/top?count=3&api_key={LOL_API_KEY}"
    mastery_data = get_api_data(CHAMP_API)

    RANKED_API = f"https://{region}1.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}?api_key={LOL_API_KEY}"
    ranked_data = get_api_data(RANKED_API)

    LIVE_GAME_API = f"https://{region}1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{summoner_id}?api_key={LOL_API_KEY}"
    is_in_game, live_data = get_live_data(LIVE_GAME_API)

    mastery = ""

    for c in range(len(mastery_data)):
        champ_name = get_champname(str(mastery_data[c]["championId"]))
        champ_point = str(mastery_data[c]["championPoints"])

        mastery = (
            mastery
            + f"{c+1}. "
            + champ_name
            + ": "
            + champ_point[:-3]
            + "."
            + champ_point[len(champ_point) - 3 :]
            + "\n"
        )

    RANKS = ["I", "II", "III", "IV", "V"]
    rank = ranked_data[1]["tier"] + " " + RANKS[len(ranked_data[1]["rank"]) - 1]
    league_point = ranked_data[1]["leaguePoints"]
    winrate = (
        int(ranked_data[1]["wins"])
        / (int(ranked_data[1]["wins"]) + int(ranked_data[1]["losses"]))
        * 100
    )

    # if player is in game get necessary data
    if is_in_game:
        game_length = float(str(live_data["gameLength"]).split(" ")[0]) / 60.0
        for participant in live_data["participants"]:
            if participant["summonerId"] == summoner_id:
                in_game_champion = participant["championId"]
                live_champ = get_champname(str(in_game_champion))
                live_data = f"Playing **{live_champ}** for {game_length:.1f} minutes."
                break
    else:
        live_data = "N/A Playing"

    summoner = Summoner(
        player_name,
        summoner_data["profileIconId"],
        summoner_data["summonerLevel"],
        rank,
        league_point,
        ranked_data[1]["wins"],
        ranked_data[1]["losses"],
        f"{winrate:.0f}",
        mastery,
        live_data,
    )

    return summoner


def createEmbed(player: Summoner) -> discord.embeds.Embed:

    message = discord.Embed(
        title=f"{player.name}", description="Here are all the stats we found:"
    )
    message.set_thumbnail(
        url=f"https://ddragon.leagueoflegends.com/cdn/12.22.1/img/profileicon/{player.icon}.png"
    )
    message.add_field(name="Level:", value=f"{player.level}")
    message.add_field(
        name="Ranked Stats:",
        value=f"{player.rank}\n**{player.league_point}LP** {player.win}W {player.lose}L\nWinrate: {player.winrate}%",
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
