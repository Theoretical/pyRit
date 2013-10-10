class Region:
    NA = ('prod.na1.lol.riotgames.com', 2099, 'na1')
    EUW = ('prod.euw.lol.riotgames.com', 2099, 'eu')
    EUNE = ('prod.eune.lol.riotgames.com', 2099, 'eune')

    @staticmethod
    def getRegion(code):
        if code == 'NA':
            return Region.NA
        elif code == 'EUW':
            return Region.EUW
        elif code == 'EUNE':
            return Region.EUNE
        else:
            return Region.NA