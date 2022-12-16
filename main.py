import discord
from requests import get
import json
import riotwatcher
from time import sleep
from bs4 import BeautifulSoup
from re import findall

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
        player_name, player_region = get_name_region(message.content)
        summoner = get_profile_data(player_name, player_region)

        bot_message = create_profile_embed(summoner)

        await message.channel.send(f"{message.author.mention} here it is!")
        await message.channel.send(embed=bot_message)

    elif message.content.startswith("!rotation"):
        rotaion_champion_names = get_rotation_data(message.content)
        bot_message = create_rotation_embed(rotaion_champion_names)

        await message.channel.send(f"{message.author.mention} here it is!")
        await message.channel.send(embed=bot_message)

    elif message.content.startswith("!counter"):
        champion = message.content[9:]
        champion = str(champion).capitalize()
        counter_champions = get_counter_data(champion)
        bot_message = create_counter_embed(counter_champions, champion)

        await message.channel.send(f"{message.author.mention} here it is!")
        await message.channel.send(embed=bot_message)

    elif message.content.startswith("!livegame"):
        player_name, player_region = get_name_region(message.content)

        (
            in_game,
            p_names,
            p_champ_names,
            p_ranks,
            p_leaguepoints,
            p_winrate,
            game_length,
        ) = get_live_game_data(player_name, player_region)

        if in_game:
            bot_message = create_live_game_embed(
                p_names, p_champ_names, p_ranks, p_leaguepoints, p_winrate, game_length
            )
            await message.channel.send(f"{message.author.mention} here it is!")
            await message.channel.send(embed=bot_message[0])
            await message.channel.send(embed=bot_message[1])
            await message.channel.send(embed=bot_message[2])

        else:
            await message.channel.send(
                f"{message.author.mention} \nSummoner **{player_name}** is not playing at the moment."
            )

    elif message.content.startswith("!quote"):
        quoute = get_quote()
        await message.channel.send(f"{message.author.mention} here it is!")
        await message.channel.send(quoute)


def create_live_game_embed(
    player_names: list[str],
    champion_names: list[str],
    player_ranks: list[str],
    league_points: list[int],
    winrates: list[str],
    game_length: str,
) -> tuple[discord.embeds.Embed, discord.embeds.Embed]:
    embed_name_blue = ""
    embed_rank_blue = ""
    for i in range(5):
        embed_name_blue = (
            embed_name_blue + f"{player_names[i]} **({champion_names[i]})**\n"
        )
        embed_rank_blue = (
            embed_rank_blue
            + f"{player_ranks[i]} ({league_points[i]}LP) **{winrates[i]}%**\n"
        )

    embed_name_red = ""
    embed_rank_red = ""
    for i in range(5, 10):
        embed_name_red = (
            embed_name_red + f"{player_names[i]} **({champion_names[i]})**\n"
        )
        embed_rank_red = (
            embed_rank_red
            + f"{player_ranks[i]} ({league_points[i]}LP) **{winrates[i]}%**\n"
        )

    main = discord.Embed(
        title=f"Live Game:",
        description=f"Playing for **{game_length}** minutes.",
        color=discord.Colour.from_rgb(248, 217, 28),
    )

    blue_message = discord.Embed(
        title="",
        description="",
        color=discord.Colour.from_rgb(0, 0, 255),
    )

    blue_message.add_field(name="Blue Team:", value=embed_name_blue)

    blue_message.add_field(
        name="Ranks/WR:",
        value=f"{embed_rank_blue}",
        inline=True,
    )
    red_message = discord.Embed(
        title="",
        description="",
        color=discord.Colour.from_rgb(255, 0, 0),
    )
    red_message.add_field(name="Red Team:", value=f"{embed_name_red}")
    red_message.add_field(
        name="Ranks/WR:",
        value=f"{embed_rank_red}",
        inline=True,
    )
    return main, blue_message, red_message


def create_rotation_embed(names: tuple[str, str]) -> discord.embeds.Embed:
    message = discord.Embed(
        title="Free Rotation",
        description="Here is this weeks rotation:",
        color=discord.Colour.from_rgb(248, 217, 28),
    )
    message.set_thumbnail(url="https://i.imgur.com/shAjLsZ.png")
    message.add_field(name="᲼᲼", value=f"**{names[0]}**")
    message.add_field(name="᲼᲼", value=f"**{names[1]}**", inline=True)
    return message


def create_counter_embed(champions: str, champion: str) -> discord.embeds.Embed:

    message = discord.Embed(
        title="Counter Champions",
        description=f"Here here are the best picks for **{champion}**:",
        color=discord.Colour.from_rgb(248, 217, 28),
    )
    if len(champion.split(" ")) > 1:
        champion = champion.split(" ")[0] + champion.split(" ")[1].capitalize()

    message.set_thumbnail(
        url=f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champion}_0.jpg"
    )
    message.add_field(name="Champions:", value=f"{champions}")

    return message


def get_live_game_data(player_name: str, region: str):

    API_URL = f"https://{region}1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{player_name}?api_key={LOL_API_KEY}"
    summoner_data = get_api_data(API_URL)

    summoner_id = summoner_data["id"]

    LIVE_GAME_API = f"https://{region}1.api.riotgames.com/lol/spectator/v4/active-games/by-summoner/{summoner_id}?api_key={LOL_API_KEY}"
    is_in_game, live_data = get_live_data(LIVE_GAME_API)

    if not is_in_game:
        return False, "", "", "", "", "", ""

    participants = live_data["participants"]

    p_names = []
    p_champ_ids = []
    p_ids = []
    p_ranks = []
    p_leaguepoints = []
    p_winrate = []

    for participant in participants:

        p_names.append(participant["summonerName"])
        p_champ_ids.append(participant["championId"])
        p_ids.append(participant["summonerId"])

    p_champ_names = get_champion_names(p_champ_ids)

    RANKS = ["I", "II", "III", "IV", "V"]

    for id in p_ids:
        RANKED_API = f"https://{region}1.api.riotgames.com/lol/league/v4/entries/by-summoner/{id}?api_key={LOL_API_KEY}"
        ranked_data = get_api_data(RANKED_API)

        try:
            rank = ranked_data[1]["tier"] + " " + RANKS[len(ranked_data[1]["rank"]) - 1]
            league_point = ranked_data[1]["leaguePoints"]
            winrate = (
                int(ranked_data[1]["wins"])
                / (int(ranked_data[1]["wins"]) + int(ranked_data[1]["losses"]))
                * 100
            )
        except:
            rank = ranked_data[0]["tier"] + " " + RANKS[len(ranked_data[0]["rank"]) - 1]
            league_point = ranked_data[0]["leaguePoints"]
            winrate = (
                int(ranked_data[0]["wins"])
                / (int(ranked_data[0]["wins"]) + int(ranked_data[0]["losses"]))
                * 100
            )

        p_leaguepoints.append(league_point)
        p_ranks.append(rank)
        p_winrate.append(f"{winrate:.0f}")

    game_length = float(str(live_data["gameLength"]).split(" ")[0]) / 60.0

    return (
        True,
        p_names,
        p_champ_names,
        p_ranks,
        p_leaguepoints,
        p_winrate,
        f"{game_length:.1f}",
    )


def create_profile_embed(player: Summoner) -> discord.embeds.Embed:

    message = discord.Embed(
        title=f"{player.name}",
        description="Here are all the stats we found:",
        color=discord.Colour.from_rgb(248, 217, 28),
    )
    message.set_thumbnail(
        url=f"https://ddragon.leagueoflegends.com/cdn/12.22.1/img/profileicon/{player.icon}.png"
    )
    message.add_field(name="Level:", value=f"{player.level}")
    message.add_field(
        name="Ranked Stats:",
        value=f"{player.rank}\n**{player.league_point}LP**\n{player.win}W {player.lose}L\nWinrate: {player.winrate}%",
        inline=True,
    )
    message.add_field(name="Top Champs:", value=f"{player.topchamps}", inline=False)
    message.add_field(name="Live Game:", value=f"{player.livegame}")

    return message


def get_counter_data(champion: str) -> str:
    champion = champion.replace(" ", "-")
    LINK = f"https://www.counterstats.net/league-of-legends/{champion}"
    resp = get(LINK)
    soup = BeautifulSoup(resp.content, "html.parser")
    data = soup.find_all("div", class_="inset")

    counter_champions = ""
    for i in range(5):
        str_data = str(data[i])

        counter = findall("(?<=square/)(.*)(?=-60x.png)", str_data)[0]
        counter = str(counter).replace("-", " ").capitalize()
        counter_champions = counter_champions + counter + "\n"

    return counter_champions


def get_rotation_data(message: str) -> tuple[str, str]:
    REGION = message.split(" ")[1]
    ROTATION_API = f"https://{REGION}1.api.riotgames.com/lol/platform/v3/champion-rotations?api_key={LOL_API_KEY}"
    # print(ROTATION_API)
    rotation_data = get_api_data(ROTATION_API)
    champions_ids = rotation_data["freeChampionIds"]
    champions_names = get_champion_names(champions_ids)

    l_champions_names_string = ""
    for i in range(8):
        l_champions_names_string = l_champions_names_string + champions_names[i] + "\n"

    r_champions_names_string = ""
    for i in range(8, 16):
        r_champions_names_string = r_champions_names_string + champions_names[i] + "\n"

    return l_champions_names_string, r_champions_names_string


def get_champion_names(ids) -> list[str]:
    resp = get(
        "http://ddragon.leagueoflegends.com/cdn/12.22.1/data/en_US/champion.json"
    )
    Data = resp.json()

    look_up = {}
    for champ in Data["data"].values():
        look_up[champ["key"]] = champ["id"]
    names = []
    for id in ids:
        names.append(look_up[str(id)])

    return names


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
        elif resp.status_code == 503:
            print(f"Error {resp.status_code} happened. Service unable.")
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
        summoner_data["name"],
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


def get_names_region(message: str) -> str:
    pass


def get_pick_data():
    pass


def get_quote() -> str:
    print("Getting Quote....")
    quoteData = get_api_data("https://zenquotes.io/api/random")
    quote = quoteData[0]["q"] + " -" + quoteData[0]["a"]
    return quote


client.run(DISCORD_TOKEN)
