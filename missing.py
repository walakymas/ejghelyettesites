#!/usr/bin/env python
import sys
from urllib.request import urlopen, Request
import re
import json
from os.path import exists
from os import environ

hooks = environ.get('HOOKS')
vibea = environ.get('VIBER')
team = environ.get('TEAM',"09(...xd|(an|ol|ne).xcdf|ol2x2ny1)")
link = environ.get('SOURCE',"https://www.ejg.hu/helyettes/")

# Ha sem Viber, sem Discord elérés nincs megadva, akkor csak teszteljük a kódot, küldés helyett kiírások
debug = not (vibea or hooks)

# A hét napjai. A terem kódok első karakterei alapján ezt jelenítjük meg.
napok = {
    'h': 'Hétfő',
    'k': 'Kedd',
    's': 'Szerda',
    'c': 'Csütörtök',
    'p': 'Péntek',
    'v': 'Vasárnap'
}

# Óra kódok. A csoport kód [2:5] része illetve a tárgy a táblázatban
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
    'foc': 'Földrajz',
    'rvk': 'Vizuális Kultúra'
}

# Sikeres mintaillesztés esetén az adatok feldolgozása
class Ora:
    def __init__(self, match):
        self.csoport = match.group(4)
        self.megjegyzes = match.group(7)
        # Csak akkor dolgozzuk fel, ha team minta illeszkedik ÉS a megjegyzés nem "-megtartja".
        # Az utóbbira azért van szükség, mert ha valakinek első órája nincs megtartva, akkor a rendszerük automatikusan
        # felveszi a további óráit mint elmaradó és külön jelezik, hogy az biza meg lesz tartva...
        self.need = re.match(team, self.csoport) and self.megjegyzes!='-megtartja'
        if self.need:
            self.datum = match.group(1)
            self.tanar = match.group(2)
            self.terem = match.group(3)
            # Human readable nap
            self.nap = napok[match.group(3)[0:1]]
            self.targykod = match.group(5)

            # Az oldal kódjának egyik furcsasága, hogy &nbsp szerepel &nbsp; helyett, a böngészők meg automatikusan
            # javítják megjelenítéskor.
            self.helyettes = match.group(6).replace("&nbsp","")
            if self.helyettes=='':
                self.helyettes = 'Nincs'

            # Human readable tanóra megjelenítés a tárgy kód alapján ha nincs a listában, akkor a tárgykódra fallback
            self.targy = orak.get(self.targykod, self.targykod)

            # Team kiokoskodása
            # - Osztott órák
            if self.csoport[7]=='1':
                self.team = 'Észak'
            elif self.csoport[7]=='2':
                self.team = 'Dél'
            # - Testnevelés
            elif self.csoport[2:10]=='tesxdfno':
                self.team = 'Lány'
            elif self.csoport[2:10]=='tesxdfff':
                self.team = 'Fiú'
            # - Nyelvi órák (ezeknél nem tudok biztonságosan szűrni arra tényleg érinti-e az osztályt.)
            elif re.match("(an|ol|ne)[12]", match.group(5)):
                self.team = 'Nyelvi'
            # - Egész osztály
            else :
                self.team = 'Osztály'

            # Amennyiben az órát online tartják
            if "online" in match.group(7):
                self.title = "Online"
                self.emoji = "computer"
                self.color = 2135072
            # Amennyiben elmarad (nincs helyettes és nem online)
            elif match.group(6) == "&nbsp":
                self.title = "Elmarad"
                self.emoji = ":heart_eyes:"
                self.color = 15844367
            # Van helyettes megadva
            else:
                self.title = "Helyettesítés"
                self.emoji = ""
                self.color = 2123412

# Küldés Viber channelre annak auth kódjával
class Viber:
    def send(self, ora:Ora):
        if vibea or debug:
            vibe = {
                "auth_token":vibea,
                "from": "3QbOontxw2C2huap/Lclww==",
                "type": "text",
                "text": f"""*{ora.title}* {ora.team} {ora.targy} {ora.nap} {ora.terem[1:2]}. óra
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

# Küldés Discord Webhook-ra
class Discord:
    def send(self, ora:Ora):
        if hooks or debug:
            e = json.dumps({"embeds": [{
                "title": ora.title +" "+ora.emoji,
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
                for hook in hooks.split(';'):
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



def main():
    if debug:
        print("DEBUG MODE")

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
            if ora.need:
                key = match.group(1)+":"+match.group(3)
                newsent.append(key)

                if key in sent:
                    print(f"Already sent {key}")
                    if not debug:
                        continue

                try:
                    Discord().send(ora)
                except Exception as e:
                    print(e)

                try:
                    Viber().send(ora)
                except Exception as e:
                    print(e)

    if not debug:
        f = open("sent.json", "w")
        f.write(json.dumps(newsent, indent=2))
        f.close()
    else:
        print(json.dumps(newsent, indent=2))

if __name__ == "__main__":
    main()