#!/usr/bin/env python
import sys
from urllib.request import urlopen, Request
import re
import json
from os.path import exists
from os import environ

hook = environ.get('HOOK')
vibea = environ.get('VIBER')
team = environ.get('TEAM',"09(...xd|(an|ol|ne).xcdf)")
link = environ.get('SOURCE',"https://www.ejg.hu/helyettes/")

debug = not (vibea or hook)

if debug:
    print("DEBUG MODE")

napok = {
    'h': 'Hétfő',
    'k': 'Kedd',
    's': 'Szerda',
    'c': 'Csütörtök',
    'p': 'Péntek',
    'v': 'Vasárnap'
}

orak = {
    'ird': 'Irodalom',
    'kem': 'Kémia',
    'an1': 'Angol1',
    'an2': 'Angol2',
    'ne1': 'Német1',
    'ne2': 'Német2',
    'ol1': 'Olasz1',
    'ol2': 'Olasz2',
    'bio': 'Biológia',
    'nyt': 'Nyelvtan',
    'mat': 'Matematika',
    'zen': 'Zene',
    'dig': 'Digitális kultúra',
    'fiz': 'Fizika',
    'ofn': 'Osztályfőnöki',
    'tes': 'Testnevelés',
    'tor': 'Történelem',
    'ola': 'Olasz',
    'ang': 'Angol',
    'nem': 'Német'
}

sent = []
newsent = []
if (exists("sent.json")):
    f = open("sent.json", "r")
    sent = json.loads(f.read())

f = urlopen(link)
myfile = f.read().decode('utf-8')
myfile = re.sub(">\n",">",myfile)
myfile = re.sub("><TR>",">\n<TR>",myfile)
for sor in myfile.splitlines():
    match = re.match("<TR><TD[^>]*>([^<]+)<\/TD> *<TD[^>]*>([^<]+)<\/TD> *<TD[^>]*>([^<]+)<\/TD> *<TD[^>]*>([^<]+)<\/TD> *<td[^>]*>([^<]+)<\/td> *<TD[^>]*>([^<]+)<\/TD> *<TD[^>]*>([^<]+)<.",sor)

    if match :
        if re.match(team, match.group(4)):
            if debug:
                print(match.group(4))
                print( match.group(7))
                print("online" in match.group(7))
            key = match.group(1)+":"+match.group(3)

            newsent.append(key)

            if match.group(4)[7]=='1':
                t = 'Észak'
            elif match.group(4)[7]=='2':
                t = 'Dél'
            else:
                t = 'Osztály'

            if key in sent:
                print(f"Already sent {key}")
                if not debug:
                    continue

            if match.group(6)=='-megtartja':
                continue

            helyettes = match.group(6).replace("&nbsp","")
            if helyettes=='':
                helyettes = 'Nincs'

            targy = orak.get(match.group(5)[0:3], match.group(5)[0:3])

            embed = {
                "title": "Helyettesítés",
                "description": match.group(1) + " " + match.group(3)[0:2] + " " + t + " " + targy + " " +  match.group(6).replace("&nbsp",""),
                "type": "rich",
                "color": 2123412,
                "fields": [
                    {"name": "Dátum", "value":match.group(1),"inline":"true"},
                    {"name": "Tanár", "value":match.group(2),"inline":"true"},
                    {"name": "Terem", "value":match.group(3),"inline":"true"},
                    {"name": "Csoport", "value":match.group(4),"inline":"true"},
                    {"name": "Tantárgy", "value":targy,"inline":"true"},
                    {"name": "Helyettes", "value":helyettes,"inline":"true"}
                ],
                "footer" : {"text":"E5vös helyettesítés info v0.1.2"}
            }

            if "online" in match.group(7):
                embed["title"] = "Online"
                embed["color"] = 2135072
            elif match.group(6) == "&nbsp":
                embed["title"] = "Elmarad"
                embed["color"] = 15844367

            e = json.dumps({"embeds": [embed]}, indent=2)

            if hook!="missing" or debug:
                jsondataasbytes = e.encode('utf-8')
                if debug:
                    print(e)
                else:
                    req = Request(
                        hook,
                        headers={
                            "Content-Type": "application/json",
                            "User-Agent": "Python",
                            "Content-Length": len(jsondataasbytes)
                        },
                        data=jsondataasbytes,
                        method="POST"
                    )
                    urlopen(req)

            if vibea or debug:
                vibe = {
                    "auth_token":vibea,
                    "from": "3QbOontxw2C2huap/Lclww==",
                    "type": "text",
                    "text": f"""*{embed['title']}* {t} {napok[match.group(3)[0:1]]} {match.group(3)[1:2]}. óra
    _{targy}_ {match.group(2)}
    Helyettes: {helyettes}
    {match.group(1)} {match.group(3)} {match.group(6).replace("&nbsp","")}"""
                }
                v = json.dumps(vibe, indent=2);
                jsondataasbytes = v.encode('utf-8')

                if debug:
                    print(v)
                else:
                    req = Request(
                        'https://chatapi.viber.com/pa/post',
                        headers={
                            "Content-Type": "application/json",
                            "Content-Length": len(jsondataasbytes)
                        },
                        data=jsondataasbytes,
                        method="POST"
                    )
                    urlopen(req)

    if not debug:
        f = open("sent.json", "w")
        f.write(json.dumps(newsent, indent=2))
        f.close()
