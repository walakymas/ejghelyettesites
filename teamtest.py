#!/usr/bin/env python
import re
from missing import orak, team

# Álmos összes órája, ezekhez férek hozzá a Krétában
teams = [
    "09an1xcdf1ddavid",
    "09bioxd1solymoss",
    "09digxd1ggkati",
    "09fizxd1farkas",
    "09focxdkedves",
    "09irdxd1flora",
    "09kemxd1matula",
    "09matxd1bujtas",
    "09nytxd1flora",
    "09ofnxdsolymoss",
    "09ol2x2ny1wmelinda",
    "09rvkxdboldizsar",
    "09tesxdfffiojozsi",
    "09torxdtar",
    "09zenxddobos"
]

for t in teams:
    if not re.match(team, t):
        print("Nem illeszkedik:" + t)
    if not t[2:5] in orak:
        print("Missing: "+t[2:5])