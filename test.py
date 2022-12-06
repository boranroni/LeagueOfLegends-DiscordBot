import json
import requests
from bs4 import BeautifulSoup
import re

LINK = "https://www.counterstats.net/league-of-legends/zyra"

resp = requests.get(LINK)

soup = BeautifulSoup(resp.content, "html.parser")

arr = soup.find_all("div", class_="inset")

for i in range(5):
    mystr = str(arr[i])
    regex = re.findall("(?<=square/)(.*)(?=-60x.png)", mystr)[0]
    print(regex)


"""


"""
