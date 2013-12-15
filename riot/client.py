from rtmp.client import RtmpClient
from riot.services import *


class LolClient:
    def __init__(self, region, user, password, version):
        self.client = RtmpClient(region, user, password, version)

    def connect(self):
        if not self.client.connect():
            return False

        self._summonerService = SummonerService(self.client)
        self._playerStatsService = PlayerStatsService(self.client)
        self._leaguesServiceProxy = LeaguesServiceProxy(self.client)
        self._gameService = GameService(self.client)
        self._loginService = LoginService(self.client)

    def getSummonerService(self):
        return self._summonerService

    def getPlayerStatsService(self):
        return self._playerStatsService

    def getLeaguesServiceProxy(self):
        return self._leaguesServiceProxy

    def getGameService(self):
        return self._gameService

    def getLoginService(self):
        return self._loginService
