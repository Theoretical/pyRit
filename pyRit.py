from flask import Flask, jsonify, Response
from riot.summoner import PublicSummoner
from riot.stats import  RecentGames
from rtmp.client import RtmpClient
from time import clock


class pyRit:
    def __init__(self, region, user, password):
        self.client = RtmpClient(region, user, password)
        self.app = Flask(__name__)
        self.buildRoutes()

    def start(self, debug=False):
        self.client.connect()
        self.app.run(threaded=True, debug=debug)

    def buildRoutes(self):
        self.app.add_url_rule('/history/<acctId>', 'history', self.getRecentGames)
        self.app.add_url_rule('/public/<acctId>', 'public', self.getAllPublicSummonerDataByAccount)
        self.app.add_url_rule('/name/<summonerName>', 'name', self.getSummonerByName)
        self.app.add_url_rule('/game/<summonerName>', 'game', self.getGameInProgress)
        self.app.add_url_rule('/ranked/<acctId>/<season>', 'ranked', self.getRankedStats, defaults={'season': 'CURRENT'})
        self.app.add_url_rule('/leagues/<summonerId>', 'leagues', self.getAllLeaguesForPlayer)
        self.app.add_url_rule('/practice/', 'practice', self.getPracticeGames)
        self.app.add_url_rule('/store/', 'store', self.getStoreUrl)
        self.app.add_url_rule('/acct/', 'acct', self.getAcctInfo)

    def waitForMessage(self, service, operation, params):
        msg = None
        invokeId = self.client.invoke(service, operation, params)
        timeOut = clock() + 10000

        while msg is None or clock() >= timeOut:
            msg = self.client.getPendingRequest(invokeId)

        return msg

    def getRecentGames(self, acctId):
        msg = self.waitForMessage('playerStatsService', 'getRecentGames', [int(float(acctId))])

        if msg == -1 or msg is None:
            return jsonify({'error': 'Invalid accountId'})

        recent = RecentGames(msg['body'])
        return Response(recent.toJson(), mimetype='application/json')

    def getAllPublicSummonerDataByAccount(self, acctId):
        msg = self.waitForMessage('summonerService', 'getAllPublicSummonerDataByAccount', [int(float(acctId))])

        if msg == -1 or msg['result'] == u'_error' or msg['body'] is None:
            return jsonify({'error': 'Invalid accountId'})

        recent = RecentGames(msg['body'])
        return jsonify(msg['body'])

    def getStoreUrl(self):
        msg = self.waitForMessage('loginService', 'getStoreUrl', [])
        return msg['body']

    def getSummonerByName(self, summonerName):
        msg = self.waitForMessage('summonerService', 'getSummonerByName', [summonerName])

        summoner = PublicSummoner(msg['body'])
        return Response(summoner.toJson(), mimetype='application/json')

    def getAcctInfo(self):
        pass

    def getGameInProgress(self, summonerName):
        pass

    def getRankedStats(self, acctId, season):
        pass

    def getAllLeaguesForPlayer(self, summoner):
        pass

    def getPracticeGames(self):
        pass


if __name__ == "__main__":
    p = pyRit('NA', 'riot2json2', 'asdasdzx123')
    p.start(True)