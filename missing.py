#!/usr/bin/env python

from urllib.request import urlopen, Request
import re
import json
from os.path import exists
from os import environ

hook = environ.get('HOOK', "missing")
team = environ.get('TEAM',"09...xd[^1]")
link = environ.get('SOURCE',"https://www.ejg.hu/helyettes/")

print(hook)
print(team)

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
    match = re.match("<TR><TD[^>]*>([^<]+)<\/TD> *<TD[^>]*>([^<]+)<\/TD> *<TD[^>]*>([^<]+)<\/TD> *<TD[^>]*>("+team+"[^<]+)<\/TD> *<td[^>]*>([^<]+)<\/td> *<TD[^>]*>([^<]+)<\/TD> *<TD[^>]*>([^<]+)<.",sor)

    if match:
        key = match.group(1)+":"+match.group(3)

        newsent.append(key)
        if key in sent:
            print(f"Already sent {key}")
            continue

        embed = {
            "title": "Helyettesítés",
            "description": match.group(1) +" "+match.group(3)[0:2]+" "+match.group(5)+" "+  match.group(7) +" @everyone",
            "type": "rich",
            "color": 2123412,
            "fields": [
                {"name": "Dátum", "value":match.group(1),"inline":"true"},
                {"name": "Tanár", "value":match.group(2),"inline":"true"},
                {"name": "Terem", "value":match.group(3),"inline":"true"},
                {"name": "Csoport", "value":match.group(4),"inline":"true"},
                {"name": "Tantárgy", "value":match.group(5),"inline":"true"},
                {"name": "Helyettes", "value":match.group(6).replace("&nbsp","-"),"inline":"true"}
            ],
            "footer" : {"text":"E5vös helyettesítés info v0.1.1"}
        }

        if match.group(6) == "&nbsp":
            embed["title"] = "Elmarad :heart_eyes:"
            embed["color"] = 15844367;

        e = json.dumps({"embeds": [embed]}, indent=2);
        jsondataasbytes = e.encode('utf-8')
        req = Request(
            hook,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "",
                "Content-Length": len(jsondataasbytes)
            },
            data=jsondataasbytes,
            method="POST"
        )
        urlopen(req, jsondataasbytes)

    f = open("sent.json", "w")
    f.write(json.dumps(newsent, indent=2))
    f.close()
