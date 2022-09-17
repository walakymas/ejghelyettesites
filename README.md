# ejghelyettesites

Eötvös József Gimnázium helyettesítések oldal 

#Rendszer beállítások:

- HOOK: Webhook Url alapértelmezés nincs, kötelezően megadni
- TEAM: Mely csoportok helyettesítéseiről küldjön üzenetet (default: '09...xd[^1]')
- SOURCE: Honnan vegye a html-t (default: 'https://www.ejg.hu/helyettes/')

# Crontab beállítások
```
HOOK= #WebhookUrl#
*/10 * * * * ${PATHTOSCRIPT}/missing.py > missing.log
```
