from flask import Flask, jsonify, Response
from riot.client import Client

class pyRit:
    def __init__(self, region, user, password):
        self.client = Client(region, user, password)
        self.app = Flask(__name__)
        self.buildRoutes()

    def start(self, debug=False):
        self.client.connect()
        self.app.run(threaded=True, debug=debug)

    def buildRoutes(self):
        self.app.add_url_rule('/history/<summoner>', 'history', self.getRecentGames)
        self.app.add_url_rule('/public/<acctId>', 'public', self.getAllPublicSummonerDataByAccount)
        self.app.add_url_rule('/name/<summonerName>', 'name', self.getSummonerByName)
        self.app.add_url_rule('/game/<summonerName>', 'game', self.getGameInProgress)
        self.app.add_url_rule('/ranked/<acctId>/<season>', 'ranked', self.getRankedStats, defaults={'season': 'CURRENT'})
        self.app.add_url_rule('/leagues/<summonerId>', 'leagues', self.getAllLeaguesForPlayer)
        self.app.add_url_rule('/practice/', 'practice', self.getPracticeGames)
        self.app.add_url_rule('/store/', 'store', self.getStoreUrl)
        self.app.add_url_rule('/acct/', 'acct', self.getAcctInfo)

    def getRecentGames(self, summoner):
        if summoner.isdigit():
            recent = self.client.getPlayerStatsService().getRecentGames(summoner)
            return Response(recent.toJson(), mimetype='application/json')
        else:
            publicSummoner = self.client.getSummonerService().getSummonerByName(summoner)
            recent = self.client.getPlayerStatsService().getRecentGames(publicSummoner.acctId)
            return Response(recent.toJson(), mimetype='application/json')

    def getAllPublicSummonerDataByAccount(self, acctId):
        pass

    def getStoreUrl(self):
        pass

    def getSummonerByName(self, summonerName):
        summoner = self.client.getSummonerService().getSummonerByName(summonerName)
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