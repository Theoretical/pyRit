from serialize import Serialize
import json


class Entry:
    def __init__(self, data):
        self.demotionWarning = data['demotionWarning']
        self.displayDecayWarning = data['displayDecayWarning']
        self.freshBlood = data['freshBlood']
        self.hotStreak = data['hotStreak']
        self.inactive = data['inactive']
        self.lastPlayed = data['lastPlayed']
        self.leagueName = data['leagueName']
        self.leaguePoints = data['leaguePoints']
        self.losses = data['losses']
        self.miniSeries = data['miniSeries']
        self.playerOrTeamId = data['playerOrTeamId']
        self.playerOrTeamName = data['playerOrTeamName']
        self.previousDayLeaguePosition = data['previousDayLeaguePosition']
        self.queueType = data['queueType']
        self.rank = data['rank']
        self.tier = data['tier']
        self.timeLastDecayMessageShown = data['timeLastDecayMessageShown']
        self.timeUntilDecay = data['timeUntilDecay']
        self.veteran = data['veteran']
        self.wins = data['wins']


class SummonerLeagues(Serialize):
    def __init__(self, body):
        self.name = body['summonerLeagues'][0]['name']
        self.tier = body['summonerLeagues'][0]['tier']

        for league in body['summonerLeagues']:
            for entry in league['entries']:
                self.entries.append(Entry(entry))