import json
import requests

f = open("keys.json")
keys = json.load(f)
LOL_API_KEY = keys["LOL_API"]





playerName = "RBD"
region = "TR1"

PLAYER_API_LINK = f"https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{playerName}?api_key={LOL_API_KEY}"


resp = requests.get(PLAYER_API_LINK)
summonerData = resp.json()


summonerPuuid = summonerData["puuid"]
matchRegion = "europe"

MATCH_API_LINK = f"https://{matchRegion}.api.riotgames.com/lol/match/v5/matches/by-puuid/{summonerPuuid}/ids?start=0&count=5&api_key={LOL_API_KEY}"


resp = requests.get(MATCH_API_LINK)
matches = resp.json()

def get_match_data(matchId):
    MATCH_INFO_API_LINK = f"https://{matchRegion}.api.riotgames.com/lol/match/v5/matches/{matchId}?api_key={LOL_API_KEY}"

    resp = requests.get(MATCH_INFO_API_LINK)
    matchData = resp.json()

    Index = int(matchData["metadata"]["participants"].index(summonerPuuid))
    Champ = matchData["info"]["participants"][Index]["championName"]
    Win = matchData["info"]["participants"][Index]["win"]
    K = matchData["info"]["participants"][Index]["kills"]
    D = matchData["info"]["participants"][Index]["deaths"]
    A = matchData["info"]["participants"][Index]["assists"]
    
    try:
      #if death is 0, math is bad, Newton is really sad  
        KDA = matchData["info"]["participants"][Index]["challenges"]["kda"]
    except:
        if D != "0": 
            KDA = ((int(A)+int(K)) / int(D))
        else:
            KDA = (int(A)+int(K))

    print(f"{Champ} {K} {D} {A} {KDA:.1f}")


    
for match in matches:
    get_match_data(match)
#https://ddragon.leagueoflegends.com/cdn/img/champion/splash/Aatrox_0.jpg
"""


{
  "content": null,
  "embeds": [
    {
      "title": "SUMMONER NAME",
      "description": "Here are all the stats we found:\n\n**Level:** ᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼**Ranked Stats:**\nlvl᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼ **Ranked 3**\n᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼  30W 32L\n᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼᲼   ᲼Winrate: 30%\n**Top Champions:**\n1.Kled : 800.00\n2.Aatrox: 200.00\n3:Rengar: 120.000\n\n**Live Game:**\nplayin or not",
      "color": 5814783,
      "thumbnail": {
        "url": "https://ddragon.leagueoflegends.com/cdn/12.22.1/img/profileicon/933.png"
      }
    }
  ],
  "attachments": []
}

"""
