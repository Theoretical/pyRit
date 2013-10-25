import base64
import datetime
import os
import rtmp.decoder
import rtmp.encoder
import threading
import time
import uuid

from gevent import ssl, spawn
from pyamf import TypedObject
from pyamf.flex.messaging import RemotingMessage, CommandMessage
from riot.region import Region
from riot.login import GetLoginToken, AuthenticationCredentials
from rtmp import defs


class RtmpClient:
    def __init__(self, regionId, user, password):
        self.version = '3.12.13_10_03_21_10'
        self.region = Region.getRegion(regionId)
        self.host = self.region[0]
        self.port = int(self.region[1])
        self.socket = None
        self.callbacks = {}
        self.pendingRequests = {}
        self.invokeId = 1
        self.encoder = rtmp.encoder.AmfEncoder()
        self.token = GetLoginToken(user, password, self.region[2])
        self.user = user
        self.password = password
        self.auth = False
        print 'Connecting to region: {0}'.format(self.region)

    def connect(self):
        self.socket = ssl.SSLSocket(ssl.socket(), ssl_version=3)
        self.socket.connect((self.host, self.port))
        self.doHandshake()
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
        threading.Thread(target=self.processMessages).start()

    def processMessages(self):
        while True:
            msg = self.reader.next()

            if msg == None:
                continue

            print 'Processing: {0}'.format(msg)
            if msg['msg'] == defs.DataTypes.COMMAND:
                self.dsid = msg['cmd'][3]['id']
                self.login(self.user, self.password)

            if msg['msg'] == defs.DataTypes.INVOKE:
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

    def heartbeatThread(self):
        heartbeatCount = 1
        while True:
            if self.auth:
                date = datetime.datetime.now().strftime("%d %m %d %Y %H:%M:%S 'GMTZ'")
                id = self.invoke('loginService', 'performLCDSHeartBeat', [self.acctId, self.session, heartbeatCount, date], None)
                del self.pendingRequests[id]
                heartbeatCount += 1
                print 'Sent heartbeat'
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

        threading.Thread(target=self.heartbeatThread).start()

    def sendMessage(self, msg):
        invokeId = self.nextInvokeId()
        invoke = self.encoder.encodeInvoke(invokeId, msg)

        self.stream.write(invoke)
        return invokeId

    def invoke(self, destination, operation, body, callback=None):
        headers = TypedObject('')

        headers['DSRequestTimeout'] = 60
        headers['DSId'] = self.dsid
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
        headers['DSId'] = self.dsid
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