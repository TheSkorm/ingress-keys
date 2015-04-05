from libmproxy.protocol.http import decoded
from libmproxy.protocol import KILL

import json

def request(context, flow):
	whitelist = ["m-dot-betaspike.appspot.com","gmaps","google","ingress","mitm.it"]
	if not any( k in flow.request.url for k in whitelist ):
		flow.reply(KILL)
def response(context, flow):
	with decoded(flow.response):
		if flow.request.url == "https://m-dot-betaspike.appspot.com/rpc/playerUndecorated/getInventory":
			jsonoutput = flow.response.content
			inventory = json.loads(jsonoutput)['gameBasket']['inventory']
			token = flow.request.headers["X-XsrfToken"][0][:12]
			"".join([c for c in token if c.isalpha() or c.isdigit() or c==' ']).rstrip()
			csvout = ""
			portals = {}
			for item in inventory:
				if 'portalCoupler' in item[2]:
					portal = {}
					portal['title'] = item[2]['portalCoupler']['portalTitle']
					portal['address'] = item[2]['portalCoupler']['portalAddress']
					portal['image'] = item[2]['portalCoupler']['portalImageUrl']
					portal['location'] = item[2]['portalCoupler']['portalLocation']
					loclat, loclng = item[2]['portalCoupler']['portalLocation'].split(",")
					loclat = int(loclat,16)
					loclng = int(loclng,16)
					if (loclat >= 2147483648):
						loclat -= 4294967296
					if (loclng >= 2147483648):
						loclng -= 4294967296
					loclng = loclng / 1E6
					loclat = loclat / 1E6
					portal['lat'] = loclat
					portal['lng'] = loclng
					portal['count'] = 1
					id = item[2]['portalCoupler']['portalGuid']
					if id not in portals:
						portals[id] = portal 
					else:
						portals[id]['count'] = portals[id]['count'] + 1

			f = open("/var/www/lighttpd/ingress-keys/" + token + ".csv", "a")
			csvout="id,title,address,image,longitude,latitude,keycount\n"
			for portal in portals:
				csvout = csvout + portal + ",\"" + portals[portal]["title"].replace("\"","") + "\",\"" + portals[portal]["address"].replace("\"","") + "\"," + portals[portal]["image"] + "," + str(portals[portal]["lng"]) + "," + str(portals[portal]["lat"]) + "," + str(portals[portal]["count"])+"\n"
			csvout = csvout.encode('utf8', 'replace')
			f.write(csvout)
			f.close()
		elif flow.request.url == "https://m-dot-betaspike.appspot.com/rpc/playerUndecorated/getPaginatedPlexts":
			token = flow.request.headers["X-XsrfToken"][0][:12]
			"".join([c for c in token if c.isalpha() or c.isdigit() or c==' ']).rstrip()
			flow.response.content = downloadmessage("http://119.9.15.56/ingress-keys/" + token + ".csv")
			print flow.response.content 


def downloadmessage(url):
	return """{
    "result": [
        [
            "e8a90eaec2ea49f5b563919e3bbd13bf.d",
            1427840920601,
            {
                "controllingTeam": {
                    "team": "ALIENS"
                },
                "plext": {
                    "text": "[secure] YOUR KEYS FILE CAN BE DOWNLOADED AT """ + url + """ ",
                    "team": "ALIENS",
                    "markup": [
                        [
                            "SECURE",
                            {
                                "plain": "[secure] "
                            }
                        ],
                        [
                            "SENDER",
                            {
                                "plain": "SYSTEM: ",
                                "guid": "e8a90eaec2ea49f5b563919e3bbd13bf.d",
                                "team": "ALIENS"
                            }
                        ],
                        [
                            "TEXT",
                            {
                                "plain": ""
                            }
                        ],
                        [
                            "AT_PLAYER",
                            {
                                "plain": "@YOU",
                                "guid": "e8a90eaec2ea49f5b563919e3bbd13bf.d",
                                "team": "ALIENS"
                            }
                        ],
                        [
                            "TEXT",
                            {
                                "plain": " YOUR KEYS FILE CAN BE DOWNLOADED AT """ + url  +  """ "
                            }
                        ]
                    ],
                    "plextType": "PLAYER_GENERATED",
                    "categories": 6
                },
                "locationE6": {
                    "latE6": -21172219,
                    "lngE6": 149184564
                }
            }
        ]
    ],
    "gameBasket": {
        "gameEntities": [],
        "inventory": [],
        "deletedEntityGuids": []
    }

}"""
