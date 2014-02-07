from flask import Flask, jsonify, Response
from json import dumps
from multiprocessing import Process, Pipe
from pyRitInstance import ClientInstance
from Queue import Queue
from riot.client import LolClient
from time import time, sleep
from threading import Thread
from version import fetch_current_version


class pyRit:
    def __init__(self, region, user, password, version):
        self.region = region
        self.userKey = user
        self.password = password
        self.version = version
        self.requests = 0
        self.clientIndex = 0

        #Setup Flask restful routes.
        self.app = Flask(__name__)
        self.buildRoutes()

    def buildRoutes(self):
        self.app.add_url_rule('/recent/<summoner>', 'history', self.getRecentGames)
        self.app.add_url_rule('/name/<summonerName>', 'name', self.getSummonerByName)
        self.app.add_url_rule('/game/<summonerName>', 'game', self.getGameInProgress)
        self.app.add_url_rule('/ranked/<summoner>/<season>', 'ranked', self.getRankedStats, defaults={'season': 'CURRENT'})
        self.app.add_url_rule('/leagues/<summoner>', 'leagues', self.getAllLeaguesForPlayer)
        self.app.before_request(self.processThrottle)

    def _throttleThread(self):
        start = time()
        REQUEST_THROTTLE = 500

        while True:
            if start <= time() + 5:
                start = time()
                if self.requests > REQUEST_THROTTLE and self.clientIndex < 50:
                    c = LolClient(self.region, '{0}{1}'.format(self.userKey, self.clientIndex), self.password, self.version)
                    p_in, p_out = Pipe()
                    p = Process(target=ClientInstance, args=(c, p_out), name='pyRit-{0}-{1}{2}'.format(self.region, self.userKey, self.clientIndex))
                    p.start()
                    self.clients.put_nowait(p_in)
                    self.clientIndex += 1

                    print 'Launched client {0} due to throttle'.format(self.clientIndex)
                    self.requests = 0
            sleep(.5)

    def processThrottle(self):
        self.requests += 1

    def createClients(self, clientCount):
        self.clients = Queue()
        for i in range(0, clientCount):
            c = LolClient(self.region, '{0}{1}'.format(self.userKey, i), self.password, self.version)
            p_in, p_out = Pipe()
            p = Process(target=ClientInstance, args=(c, p_out), name='pyRit-{0}-{1}{2}'.format(self.region, self.userKey, i))

            p.start()
            self.clients.put_nowait(p_in)
            self.clientIndex += 1
            print 'Launched client: {0}'.format(i)

    def start(self, clientCount, debug=False):
        self.createClients(clientCount)
        Thread(target=self._throttleThread).start()
        self.app.run(host='0.0.0.0', threaded=True, debug=debug)

    def nextClient(self):
        c = self.clients.get(False)
        self.clients.put_nowait(c)
        return c

    def invoke(self, operation, args):
        client = self.nextClient()
        client.send([operation, args])
        return client.recv()

    def getSummonerByName(self, summonerName):
        summoner = self.invoke('name', [summonerName])
        return Response(summoner.toJson(), mimetype='application/json')

    def getRecentGames(self, summoner):
        if summoner.isdigit():
            recent = self.invoke('recent', [summoner])
            return Response(recent.toJson(), mimetype='application/json')
        else:
            publicSummoner = self.invoke('name', [summoner])
            recent = self.invoke('recent', [publicSummoner.acctId])
            return Response(recent.toJson(), mimetype='application/json')

    def getGameInProgress(self, summonerName):
        game = self.invoke('game', [summonerName])
        return Response(dumps(game, sort_keys=True, indent=4), mimetype='application/json')

    def getRankedStats(self, summoner, season):
        pass

    def getAllLeaguesForPlayer(self, summoner):
        if summoner.isdigit():
            leagues = self.invoke('leagues', [summoner])
            return Response(leagues.toJson(), mimetype='application/json')
        else:
            publicSummoner = self.invoke('name', [summoner])
            leagues = self.invoke('leagues', [publicSummoner.summonerId])
            return Response(leagues.toJson(), mimetype='application/json')


if __name__ == '__main__':
    version = fetch_current_version()
    p = pyRit('NA', 'pyrit', 'asdasdzx123', version)
    p.start(1)
