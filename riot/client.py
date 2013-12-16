from rtmp.client import RtmpClient
from riot.services import *


class LolClient:
    def __init__(self, region, user, password, version):
        self._client = RtmpClient(region, user, password, version)

    def connect(self):
        if not self._client.connect():
            return False

        self._summonerService = SummonerService(self._client)
        self._playerStatsService = PlayerStatsService(self._client)
        self._leaguesServiceProxy = LeaguesServiceProxy(self._client)
        self._gameService = GameService(self._client)
        self._loginService = LoginService(self._client)

    def getRTMPClient(self):
        return self._client

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
