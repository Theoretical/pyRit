from riot.summoner import PublicSummoner
from riot.stats import  RecentGames
from rtmp.client import RtmpClient
from riot.services import *

class Client:
    def __init__(self, region, user, password):
        self.client = RtmpClient(region, user, password)

    def connect(self):
        if not self.client.connect():
            return False

        self._summonerService = SummonerService(self.client)
        self._playerStatsService = PlayerStatsService(self.client)

    def getSummonerService(self):
        return self._summonerService

    def getPlayerStatsService(self):
        return self._playerStatsService