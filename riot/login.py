import urllib
import urllib2
import json
import time
import pyamf

def GetLoginToken(user, password, region):
    req = urllib2.Request('https://lq.{0}.lol.riotgames.com/login-queue/rest/queue/authenticate'.format(region))
    res = urllib2.urlopen(req, 'payload=user={0},password={1}'.format(urllib.quote_plus(user), urllib.quote_plus(password)))
    args = json.loads(res.read())

    if 'token' in args:
        return args['token']

    if args['reason'] == 'OpeningSite':
        print 'Server is currently busy, please hold!'
        time.sleep(args["delay"])
        return GetLoginToken(user, password, region)

    if args['reason'] == 'login_rate':
        print 'Currently in login queue, please hold!'

        node = args['node']
        champ = args["champ"]
        rate = args["rate"]
        delay = args["delay"]
        id = -1
        cur = -1

        for tick in args['tickers']:
            if tick['node'] == node:
                id = tick['id']
                cur = tick['current']

        while id - cur > rate:
            print 'Currently in position: {0} |  delay: {1}'.format(id - cur, delay)

            time.sleep(delay)
            req = urllib2.urlopen('https://lq.{0}.lol.riotgames.com/login-queue/rest/queue/ticker/{1}'.format(region, champ))
            args = json.loads(req.read())

            cur = int(args[str(node)])

        if 'token' in args:
            return args['token']

        if  id - cur < 0:
            time.sleep(delay/100)

        while True:
            try:
                req = urllib2.urlopen('https://lq.{0}.lol.riotgames.com/login-queue/rest/queue/authToken/{1}'.format(region, user.lower()))
                break
            except urllib2.HTTPError:
                continue
        return json.loads(req.read())['token']


class RemoteClass(object):
    def __init__(self, alias):
        self.alias = alias

    def __call__(self, classType):
        pyamf.register_class(classType, self.alias)
        return classType


@RemoteClass(alias='com.riotgames.platform.login.AuthenticationCredentials')
class AuthenticationCredentials:
    def __init__(self, *args, **kwargs):
        self.username = args[0]
        self.password = args[1]
        self.authToken = args[2]
        self.clientVersion = args[3]
        self.ipAddress = '127.0.01'
        self.locale = 'en_US'
        self.domain = 'lolclient.lol.riotgames.com'
        self.operatingSystem = 'pyRit'
        self.securityAnswer = ''
        self.oldPassword = ''



