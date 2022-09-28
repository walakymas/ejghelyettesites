# ejghelyettesites

Eötvös József Gimnázium helyettesítések oldal figyelése és értesítés küldése webhookon keresztül egy 
Discord csatornára. Csak a Python mellett rendszerint alapból megtalálható libeket használtam (os, re, urllib, json),
hogy egyszerűbben futtatható legyen.

#Rendszer beállítások:

- HOOK: Webhook Url alapértelmezés nincs, kötelezően megadni
- TEAM: Mely csoportok helyettesítéseiről küldjön üzenetet (default: '09...xd[^2]' ami a 9D 'Észak')
- SOURCE: Honnan vegye a html-t (default: 'https://www.ejg.hu/helyettes/', teszteléskor egy 
  mentett példányt használok 'file:///home/######/helyettes.html' url-l)

# Crontab beállítások minta
```
HOOK= #WebhookUrl#
*/10 * * * * ${PATHTOSCRIPT}/missing.py > missing.log
```

# TODO

- Több webhook és minta kezelése?
- Futtatás Windows környezetben?