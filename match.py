import base64
import json
import sys
import urllib2
from riot.client import LolClient
from pyamf.amf0 import Decoder
from time import sleep, clock


def getMatch(name):
    c = LolClient('NA', 'riot2json2', 'asdasdzx123', '3.15.13_12_12_05_41')
    c.connect()

    while not c.client.auth:
        sleep(.1)

    stats = c.getGameService().retrieveInProgressSpectatorGameInfo(name)

    if stats is None:
        print 'User is not in game.'
        sys.exit()

    return int(stats["game"]["id"])

#alternative method, download the full spectator stream?


def getEndOfStats(regionShort, region, match):
    try:
        data = urllib2.urlopen('http://spectator.{0}.lol.riotgames.com:8088/observer-mode/rest/consumer/endOfGameStats/{1}/{2}/null'.
            format(regionShort, region, match)).read()

        return base64.b64decode(data)
    except urllib2.HTTPError as e:
        if e.code == 500:
            return
        else:
            return -1


match = getMatch('Blackyy')
timeOut = clock() + 3600
stats = None

print 'Polling game: {0}'.format(match),
while True:
    print '.',
    stats = getEndOfStats('na', 'NA1', match)

    if stats == -1:
        print 'An unknown error occurred.'
        sys.exit()

    if stats is not None:
        break

    sleep(30)

    if timeOut <= clock():
        print 'Game timed out!'
        exit()

decoder = Decoder(stats)
obj = decoder.readAMF3()
print json.dumps(obj, sort_keys=True, indent=4)