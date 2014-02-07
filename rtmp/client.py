import base64
import datetime
import os
import rtmp.decoder
import rtmp.encoder
import time
import uuid

from pyamf import TypedObject
from pyamf.flex.messaging import RemotingMessage, CommandMessage
from riot.region import Region
from riot.login import GetLoginToken, AuthenticationCredentials
from ssl import SSLSocket, socket, SSLError
from threading import Thread


class RtmpClient:
    socket = None
    invokeId = 1
    auth = False
    connected = False
    callbacks = {}
    pendingRequests = {}

    def __init__(self, regionId, user, password, version):
        self.region = Region.getRegion(regionId)
        self.user = user
        self.password = password
        self.version = version

        self.host = self.region[0]
        self.port = int(self.region[1])
        self.encoder = rtmp.encoder.AmfEncoder()

    def connect(self):
        print 'Connecting to region: {0}'.format(self.region)

        self.token = GetLoginToken(self.user, self.password, self.region[2])
        self.socket = SSLSocket(socket(), ssl_version=3)
        self.socket.connect((self.host, self.port))
        self.connected = True

        if not self.doHandshake():
            return False

        self.socket.setblocking(0)
        self.stream = rtmp.decoder.FileBuffer(self.socket.makefile())
        self.reader = rtmp.decoder.PacketReader(self.stream)

        msg = {
            'videoCodecs': 252,
            'audioCodecs': 3575,
            'flashVer': u'WIN 10,6,602,161',
            'app': '',
            'tcUrl': 'rtmps://{0}:2099'.format(self.host),
            'videoFunction': 1,
            'capabilities': 239,
            'pageUrl': '',
            'fpad': False,
            'swfUrl': 'app:/LolClient.swf/[[DYNAMIC]]/32',
            'objectEncoding': 3
        }

        stream = self.encoder.encodeConnect(msg)

        self.writeBytes(stream)
        self.processThread = Thread(target=self._processMessages)
        self.processThread.start()

        return True

    def _processMessages(self):
        while True:
            try:
                msg = self.reader.next()
            except SSLError as e:
                print 'An error occurred while attempting to read: {0}'.format(e)
                break

            if msg is None:
                time.sleep(.1)
                continue

            # RTMP initial login
            if msg['msg'] == rtmp.decoder.DataTypes.COMMAND:
                self.dsId = msg['cmd'][3]['id']
                self.login(self.user, self.password)

            if msg['msg'] == rtmp.decoder.DataTypes.INVOKE:
                invokeId = msg['cmd'][1]
                if invokeId in self.callbacks:
                    self.callbacks[invokeId](msg['cmd'][0], msg['cmd'][3])
                    del self.callbacks[invokeId]
                if invokeId in self.pendingRequests:
                    self.pendingRequests[invokeId] = msg


    def getPendingRequest(self, invokeId):
        if invokeId in self.pendingRequests:
            msg = self.pendingRequests[invokeId]

            if msg is None:
                return None

            return {'result': msg['cmd'][0], 'body': msg['cmd'][3].body}
        return -1

    def _heartbeatThread(self):
        heartbeatCount = 1
        while True:
            if self.auth:
                date = datetime.datetime.now().strftime("%d %m %d %Y %H:%M:%S 'GMTZ'")
                id = self.invoke('loginService', 'performLCDSHeartBeat', [self.acctId, self.session, heartbeatCount, date], None)
                del self.pendingRequests[id]
                heartbeatCount += 1

                time.sleep(12)

    def login(self, user, password):
        auth = AuthenticationCredentials(user, password, self.token, self.version)
        self.invoke('loginService', 'login', auth, self.onLogin)

    def onLogin(self, result, msg):
        if result == u'_error':
            print 'Login failed :('
            return

        self.acctId = msg.body['accountSummary']['accountId']
        self.session = msg.body['token']

        msg = self.invokeCommandMessage('auth', CommandMessage.LOGIN_OPERATION, base64.encodestring('{0}:{1}'.format(self.user, self.session)))

        msg.headers['DSSubtopic'] = 'bc'
        msg.clientId = 'bc-{0}'.format(self.acctId)
        self.sendMessage(msg)

        msg.headers['DSSubtopic'] = 'cn'
        msg.clientId = 'cn-{0}'.format(self.acctId)
        self.sendMessage(msg)

        msg.headers['DSSubtopic'] = 'gn'
        msg.clientId = 'gn-{0}'.format(self.acctId)
        self.sendMessage(msg)
        self.auth = True

        self.invoke('summonerService', 'getAllSummonerDataByAccount', [self.acctId], self.onSummonerData)

        print 'Authenticated as user: {0}'.format(self.user)
        Thread(target=self._heartbeatThread).start()

    def onSummonerData(self, result, msg):
        if result == u'_error' or msg.body == None:
            print 'Not summoner set, creating default now so we can use gameService.'
            self.invoke('summonerService', 'createDefaultSummoner', [self.user])
            return

        if msg.body['summoner']['name'] is None:
            print 'Not summoner set, creating default now so we can use gameService.'
            self.invoke('summonerService', 'createDefaultSummoner', [self.user])

    def sendMessage(self, msg):
        invokeId = self.nextInvokeId()
        invoke = self.encoder.encodeInvoke(invokeId, msg)

        self.stream.write(invoke)
        return invokeId

    def invoke(self, destination, operation, body, callback=None):
        headers = TypedObject('')

        headers['DSRequestTimeout'] = 60
        headers['DSId'] = self.dsId
        headers['DSEndpoint'] = 'my-rtmps'

        msg = RemotingMessage(destination=destination, operation=operation, body=body, headers=headers, messageId=str(uuid.uuid4()))

        if callback is not None:
            self.callbacks[self.sendMessage(msg)] = callback
        else:
            invokeId = self.sendMessage(msg)
            self.pendingRequests[invokeId] = None
            return invokeId

    def invokeCommandMessage(self, destination, operation, body):
        headers = TypedObject('')

        headers['DSRequestTimeout'] = 60
        headers['DSId'] = self.dsId
        headers['DSEndpoint'] = 'my-rtmps'

        msg = CommandMessage(destination=destination, operation=operation, body=body, headers=headers, messageId=str(uuid.uuid4()))
        invokeId = self.nextInvokeId()
        invoke = self.encoder.encodeInvoke(invokeId, msg)

        self.stream.write(invoke)

        return msg

    def nextInvokeId(self):
        self.invokeId += 1
        return self.invokeId

    def readBytes(self, size):
        return bytearray(self.socket.read(size))

    def writeBytes(self, data):
        return self.socket.write(data)

    def doHandshake(self):
        syn = bytearray(os.urandom(1537))
        syn[0] = 3

        self.writeBytes(syn)

        version = self.readBytes(1)

        if version[0] != 3:
            print "Invalid server version received"
            return False

        ack = self.readBytes(1536)
        self.writeBytes(ack)

        ack = self.readBytes(1536)

        i = 8
        while i < 1536:
            if syn[i + 1] != ack[i]:
                print 'Invalid ack!'
                return False
            i += 1

        return True