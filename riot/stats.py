import serialize


class Statistics:
    def __init__(self, data):
        self.statType = data['statType']
        self.value = data['value']
        self.dataVersion = data['dataVersion']
        self.futureData = data['futureData']


class FellowPlayers:
    def __init__(self, data):
        self.championId = data['championId']
        self.dataVersion = data['dataVersion']
        self.futureData = data['futureData']
        self.summonerId = int(data['summonerId'])
        self.teamId = data['teamId']


class GameStatistics:
    def __init__(self, data):
        self.KCoefficient = data['KCoefficient']
        self.adjustedRating = data['adjustedRating']
        self.afk = data['afk']
        self.boostIpEarned = data['boostIpEarned']
        self.boostXpEarned = data['boostXpEarned']
        self.championId = data['championId']
        self.createDate = str(data['createDate'])
        self.dataVersion = data['dataVersion']
        self.difficulty = data['difficulty']
        self.difficultyString = data['difficultyString']
        self.eligibleFirstWinOfDay = data['eligibleFirstWinOfDay']
        self.eloChange = data['eloChange']
        self.experienceEarned = data['experienceEarned']
        self.futureData = data['futureData']
        self.gameId = data['gameId']
        self.gameMapId = data['gameMapId']
        self.gameMode = data['gameMode']
        self.gameType = data['gameType']
        self.gameTypeEnum = data['gameTypeEnum']
        self.id = data['id']
        self.invalid = data['invalid']
        self.ipEarned = data['ipEarned']
        self.leaver = data['leaver']
        self.level = data['level']
        self.predictedWinPct = data['predictedWinPct']
        self.premadeSize = data['premadeSize']
        self.premadeTeam = data['premadeTeam']
        self.queueType = data['queueType']
        self.ranked = data['ranked']
        self.rating = data['rating']
        self.rawStatsJson = data['rawStatsJson']
        self.skinIndex = data['skinIndex']
        self.skinName = data['skinName']
        self.spell1 = data['spell1']
        self.spell2 = data['spell2']
        self.subType = data['subType']
        self.summonerId = data['summonerId']
        self.teamId = data['teamId']
        self.teamRating = data['teamRating']
        self.timeInQueue = data['timeInQueue']
        self.userId = data['userId']
        self.userServerPing = data['userServerPing']

        self.fellowPlayers = []
        self.statistics = []

        for player in data['fellowPlayers']:
            self.fellowPlayers.append(FellowPlayers(player))

        for stat in data['statistics']:
            self.statistics.append(Statistics(stat))


class RecentGames(serialize.Serialize):
    def __init__(self, body):
        self.gameStatistics = []
        for node in body['gameStatistics']:
            self.gameStatistics.append(GameStatistics(node))

        pass

