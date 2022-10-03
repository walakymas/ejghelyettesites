#!/usr/bin/env python

from flask import Flask, request, Response
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest

import time
import logging
import sched
import threading
from urllib.request import urlopen, Request
import re
import json
from os.path import exists
from os import environ

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

app = Flask(__name__)

@app.route('/', methods=['POST'])
def incoming():
    logger.debug("received request. post data: {0}".format(request.get_data()))
    viber_request = viber.parse_request(request.get_data())
    # handle the request here
    if isinstance(viber_request, ViberMessageRequest):
        message = viber_request.message
        # lets echo back
        logger.info(message.sender.id)
    return Response(status=200)

hook = environ.get('HOOK', "missing")
vibera = environ.get('VIBER', "missing")
team = environ.get('TEAM',"09...xd")
link = environ.get('SOURCE',"https://www.ejg.hu/helyettes/")

bot_configuration = BotConfiguration(
    name='EjgHelyettesites',
    avatar='https://www.ejg.hu/e5logo.png',
    auth_token=vibera
)
viber = Api(bot_configuration)

print(hook)
print(team)


def set_webhook(viber):
    viber.set_webhook('https://svohome.duckdns.org/ejgtest/')
    aci = viber.get_account_info();
    logger.log('')
    text_message = TextMessage(text="sample text message!")
    viber.send_messages('SzRDG8vfuQ4RCFYKHbEMJQ==', [
        text_message
    ])

def parse():

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

            if match.group(4)[7]=='1':
                t = 'Észak'
            elif match.group(4)[7]=='2':
                t = 'Dél'
            else:
                t = 'Osztály'

            if key in sent:
                print(f"Already sent {key}")
                continue

            embed = {
                "title": "Helyettesítés",
                "description": match.group(1) + " " + match.group(3)[0:2] + " " + t + " " + match.group(5) + " " +  match.group(7),
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

if __name__ == "__main__":
    scheduler = sched.scheduler(time.time, time.sleep)
    scheduler.enter(5, 1, set_webhook, (viber,))
    t = threading.Thread(target=scheduler.run)
    t.start()

    app.run(host='0.0.0.0', port=8888, debug=True)

