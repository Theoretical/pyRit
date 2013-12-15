import serialize


class PublicSummoner(serialize.Serialize):
    def __init__(self, body, clientUser):
        self.client = {{'User': clientUser}}
        self.internalName = body['internalName']
        self.name = body['name']
        self.dataVersion = body['dataVersion']
        self.revisionId = body['revisionId']
        self.futureData = body['futureData']
        self.profileIconId = body['profileIconId']
        self.summonerLevel = body['summonerLevel']
        self.acctId = body['acctId']
        self.summonerId = body['summonerId']
        self.revisionDate = str(body['revisionDate'])

