#!/usr/bin/env python

from urllib.request import urlopen, Request
import re
import json
from os.path import exists

sent = []
newsent = []
if (exists("sent.json")):
    f = open("sent.json", "r")
    sent = json.loads(f.read())

link = "https://www.ejg.hu/helyettes/"
f = urlopen(link)
myfile = f.read().decode('utf-8')
myfile = re.sub(">\n",">",myfile)
myfile = re.sub("><TR>",">\n<TR>",myfile)
for sor in myfile.splitlines():
    match = re.match("<TR><TD[^>]*>([^<]+)<\/TD> *<TD[^>]*>([^<]+)<\/TD> *<TD[^>]*>([^<]+)<\/TD> *<TD[^>]*>(09...xd[^2][^<]+)<\/TD> *<td[^>]*>([^<]+)<\/td> *<TD[^>]*>([^<]+)<\/TD> *<TD[^>]*>([^<]+)<.",sor)

    if match:
        key = match.group(1)+":"+match.group(3)

        newsent.append(key)
        if key in sent:
            print(f"Already sent {key}")
            continue

        embed = {
            "title": "Helyettesítés",
            "type": "rich",
            "color": 2123412,
            "fields": [
                {"name": "Dátum", "value":match.group(1),"inline":"true"},
                {"name": "Tanár", "value":match.group(2),"inline":"true"},
                {"name": "Terem", "value":match.group(3),"inline":"true"},
                {"name": "Csoport", "value":match.group(4),"inline":"true"},
                {"name": "Tantárgy", "value":match.group(5),"inline":"true"},
                {"name": "Helyettes", "value":match.group(6).replace("&nbsp","-"),"inline":"true"},
                {"name": "Megjegyzés", "value":match.group(7),"inline":"true"}
            ],
            "footer" : {"text":"E5vös helyettesítés info v0.1"}
        }

        if match.group(6) == "&nbsp":
            embed["title"] = "Elmarad :heart_eyes:"
            embed["color"] = 15844367;

        e = json.dumps({"embeds": [embed] }, indent=2);
        jsondataasbytes = e.encode('utf-8')
        req = Request(
            "https://discord.com/api/webhooks/1020048655316697199/x17tlxq8SQyo7jZEQMoIVkadD9jD0-v3t-JVNoXQJFPVed_wVP-j8Uravr3O-SU6eDgU",
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
