from flask import Flask, jsonify, Response
from multiprocessing import Process
from riot.client import LolClient
from time import sleep
import json

def launchClient(client):
    client.connect()

class pyRit:
    clients = []
    clientIndex = 0

    def __init__(self, region, user, password, version):
        self.region = region
        self.userKey = user
        self.password = password
        self.version = version

        #Setup Flask RESTful routes.
        self.app = Flask(__name__)
        self.buildRoutes()

    def createClients(self, clientCount):
        for i in range(0, clientCount):
            c = LolClient(self.region, '{0}{1}'.format(self.userKey, i), self.password, self.version)
            p = Process(target=launchClient, args={c})
            p.start()
            self.clients.append(c)
            print 'Launched client: {0}'.format(i)

    def start(self, clientCount, debug=False):
        self.createClients(clientCount)

        for i in range(0, len(self.clients)):
            c = self.clients[i]
            print '{0} Waiting on auth...'.format(i)
            while not c.client.auth:
                sleep(.1)

        self.app.run(threaded=True, debug=debug)

    def nextClient(self):
        c = self.clients[self.clientIndex]
        if self.clientIndex == len(self.clients):
            self.clientIndex = 0
        else:
            self.clientIndex += 1
        return c

    def buildRoutes(self):
        self.app.add_url_rule('/history/<summoner>', 'history', self.getRecentGames)
        self.app.add_url_rule('/public/<acctId>', 'public', self.getAllPublicSummonerDataByAccount)
        self.app.add_url_rule('/name/<summonerName>', 'name', self.getSummonerByName)
        self.app.add_url_rule('/game/<summonerName>', 'game', self.getGameInProgress)
        self.app.add_url_rule('/ranked/<acctId>/<season>', 'ranked', self.getRankedStats, defaults={'season': 'CURRENT'})
        self.app.add_url_rule('/leagues/<summonerName>', 'leagues', self.getAllLeaguesForPlayer)
        self.app.add_url_rule('/store', 'store', self.getStoreUrl)

    def getStoreUrl(self):
        return self.nextClient().getLoginService().getStoreUrl()

    def getRecentGames(self, summoner):
        if summoner.isdigit():
            recent = self.nextClient().getPlayerStatsService().getRecentGames(summoner)
            return Response(recent.toJson(), mimetype='application/json')
        else:
            publicSummoner = self.nextClient().getSummonerService().getSummonerByName(summoner)
            recent = self.nextClient().getPlayerStatsService().getRecentGames(publicSummoner.acctId)
            return Response(recent.toJson(), mimetype='application/json')

    def getAllPublicSummonerDataByAccount(self, acctId):
        pass

    def getSummonerByName(self, summonerName):
        summoner = self.nextClient().getSummonerService().getSummonerByName(summonerName)
        return Response(summoner.toJson(), mimetype='application/json')

    def getGameInProgress(self, summonerName):
        game = self.nextClient().getGameService().retrieveInProgressSpectatorGameInfo(summonerName)
        return Response(json.dumps(game, sort_keys=True, indent=4), mimetype='application/json')

    def getRankedStats(self, acctId, season):
        pass

    def getAllLeaguesForPlayer(self, summonerName):
        if summonerName.isdigit():
            return jsonify(self.nextClient().getLeaguesServiceProxy().getAllLeaguesForPlayer(summonerName))
        else:
            publicSummoner = self.nextClient().getSummonerService().getSummonerByName(summonerName)
            return jsonify(self.nextClient().getLeaguesServiceProxy().getAllLeaguesForPlayer(publicSummoner.summonerId))


if __name__ == "__main__":
    p = pyRit('NA', 'pyrit', 'asdasdzx123', '3.15.13_12_12_05_41')
    p.start(50)