#!/usr/bin/env python
import sys
from urllib.request import urlopen, Request
import re
import json
from os.path import exists
from os import environ

hook = environ.get('HOOK')
vibea = environ.get('VIBER')
#team = environ.get('TEAM',"09(...xd|(an|ol|ne).x)")
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
    'nem': 'Német',
    'foc': 'Földrajz'
}

class Ora:
    def __init__(self, match):
        self.datum = match.group(1)
        self.tanar = match.group(2)
        self.terem = match.group(3)
        self.nap = napok[match.group(3)[0:1]]
        self.csoport = match.group(4)
        self.megjegyzes = match.group(7)
        self.helyettes = match.group(6).replace("&nbsp","")
        if self.helyettes=='':
            self.helyettes = 'Nincs'

        self.targy = orak.get(match.group(5)[0:3], match.group(5)[0:3])

        if self.csoport[7]=='1':
            self.team = 'Észak'
        elif self.csoport[7]=='2':
            self.team = 'Dél'
        elif self.csoport[2:10]=='tesxdfno':
            self.team = 'Lány'
        elif self.csoport[2:10]=='tesxdfff':
            self.team = 'Fiú'
        else :
            self.team = 'Osztály'


        if "online" in match.group(7):
            self.title = "Online"
            self.emoji = ""
            self.color = 2135072
        elif match.group(6) == "&nbsp":
            self.title = "Elmarad"
            self.emoji = ""
            self.color = 15844367
        else:
            self.title = "Helyettesítés"
            self.emoji = ""
            self.color = 2123412

    def need(self):
        return re.match(team, self.csoport) and self.megjegyzes!='-megtartja'

class Viber:
    def send(self, ora:Ora):
        if vibea or debug:
            vibe = {
                "auth_token":vibea,
                "from": "3QbOontxw2C2huap/Lclww==",
                "type": "text",
                "text": f"""*{ora.title}* {ora.team} {ora.targy} {ora.nap} {match.group(3)[1:2]}. óra
Tanár: {ora.tanar}
Helyettes: {ora.helyettes}
{ora.datum} {ora.terem} {ora.megjegyzes}"""
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


class Discord:
    def send(self, ora:Ora):
        if hook!="missing" or debug:
            e = json.dumps({"embeds": [{
                "title": ora.title,
                "description": ora.datum + " " + ora.terem[0:2] + " " + ora.team + " " + ora.targy + " " +  ora.megjegyzes,
                "type": "rich",
                "color": ora.color,
                "fields": [
                    {"name": "Dátum", "value":ora.datum,"inline":"true"},
                    {"name": "Tanár", "value":ora.tanar,"inline":"true"},
                    {"name": "Terem", "value":ora.terem,"inline":"true"},
                    {"name": "Csoport", "value":ora.csoport,"inline":"true"},
                    {"name": "Tantárgy", "value":ora.targy,"inline":"true"},
                    {"name": "Helyettes", "value":ora.helyettes,"inline":"true"}
                ],
                "footer" : {"text":"E5vös helyettesítés info v0.1.2"}
            }]}, indent=2)
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
        ora = Ora(match)
        if ora.need():
            key = match.group(1)+":"+match.group(3)
            newsent.append(key)

            if key in sent:
                print(f"Already sent {key}")
                if not debug:
                    continue

            Discord().send(ora)
            Viber().send(ora)

if not debug:
    f = open("sent.json", "w")
    f.write(json.dumps(newsent, indent=2))
    f.close()
else:
    print(json.dumps(newsent, indent=2))

