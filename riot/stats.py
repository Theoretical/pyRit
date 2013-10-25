import serialize


class Statistics:
    def __init(self, data):
        pass


class FellowPlayers:
    def __init__(self, data):
        pass


class GameStatistics:
    def __init__(self, data):
        pass


class RecentGames(serialize.Serialize):
    def __init__(self, body):
        self.gameStatistics = []
        for node in body['gameStatistics']:
            self.gameStatistics.append(node)

        pass

