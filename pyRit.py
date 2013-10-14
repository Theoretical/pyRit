from flask import Flask, jsonify, Response
from riot.summoner import PublicSummoner
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

        return jsonify(msg['body'])

    def getAllPublicSummonerDataByAccount(self, acctId):
        msg = self.waitForMessage('summonerService', 'getAllPublicSummonerDataByAccount', [int(float(acctId))])

        if msg == -1 or msg['result'] == u'_error' or msg['body'] is None:
            return jsonify({'error': 'Invalid accountId'})

        return jsonify(msg['body'])

    def getSummonerByName(self, summonerName):
        msg = self.waitForMessage('summonerService', 'getSummonerByName', [summonerName])

        summoner = PublicSummoner(msg['body'])
        return Response(summoner.toJson(), mimetype='application/json')

if __name__ == "__main__":
    p = pyRit('NA', 'user', 'pass')
    p.start(True)