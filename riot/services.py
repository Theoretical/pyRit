from time import clock
from riot.summoner import PublicSummoner
from riot.stats import RecentGames

class BaseService:
    def __init__(self, client):
        self.client = client

    def waitForMessage(self, service, operation, params):
        msg = None
        invokeId = self.client.invoke(service, operation, params)
        timeOut = clock() + 10000

        while msg is None or clock() >= timeOut:
            msg = self.client.getPendingRequest(invokeId)

        return msg


class SummonerService(BaseService):
    def __init__(self, client):
        BaseService.__init__(self, client)
        self.name = 'summonerService'

    def getSummonerByName(self, name):
        msg = self.waitForMessage(self.name, 'getSummonerByName', [name])
        return PublicSummoner(msg['body'])

    def getSummonerNames(self, acctList):
        msg = self.waitForMessage(self.name, 'getSummonerNames', [acctList])
        return msg['body']

    def getAllPublicSummonerDataByAccount(self, acctId):
        msg = self.waitForMessage(self.name, 'getAllPublicSummonerDataByAccount', [acctId])
        return msg


class PlayerStatsService(BaseService):
    def __init__(self, client):
        BaseService.__init__(self, client)
        self.name = 'playerStatsService'

    def getRecentGames(self, acctId):
        msg = self.waitForMessage(self.name, 'getRecentGames', [acctId])
        return RecentGames(msg['body'])

    def getAggregatedStats(self, acctId, season):
        msg = self.waitForMessage(self.name, 'getAggregatedStats', [acctId, season])
        return msg

