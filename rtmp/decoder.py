import pyamf
import pyamf.util.pure
from pyamf import amf0


class Header:
    def __init__(self, channelId, timestamp=-1, dataType=-1,
                 bodyLength=-1, streamId=-1, full=False):
        self.channelId = channelId
        self.timestamp = timestamp
        self.dataType = dataType
        self.bodyLength = bodyLength
        self.streamId = streamId
        self.full = full

    @staticmethod
    def decode(data):
        channel = data.read_uchar()
        bits = channel >> 6
        channel &= 0x3f

        if channel == 0:
            channel = data.read_uchar() + 64

        if channel == 1:
            channel = data.read_uchar() + 64 + (data.read_uchar() << 8)

        header = Header(channel)
        if bits == 3:
            return header

        header.timestamp = data.read_24bit_uint()

        if bits < 2:
            header.bodyLength = data.read_24bit_uint()
            header.dataType = data.read_uchar()

        if bits < 1:
            data.endian = '<'
            header.streamId = data.read_ulong()
            data.endian = '!'

            header.full = True

        if header.timestamp == 0xffffff:
            header.timestamp = data.read_ulong()

        return header


class FileBuffer(pyamf.util.pure.DataTypeMixIn):
    def __init__(self, fd):
        self.fileobject = fd
        pyamf.util.pure.DataTypeMixIn.__init__(self)

    def read(self, length):
        return self.fileobject._sock.recv(length)

    def write(self, data):
        self.fileobject._sock.write(data)

    def flush(self):
        self.fileobject.flush()

    def at_eof(self):
        return False

    def seek(self, start, pos):
        print len(self.read(1))
        print 'Seek to: {0}'.format(pos)

    def fd(self):
        return self.fileobject


class PacketReader:
    chunkSize = 128

    def __init__(self, stream):
        self.stream = stream

    def next(self):
        if self.stream.at_eof():
            return StopIteration

        msg = []
        msgLen = 0
        try:
            header = Header.decode(self.stream)
        except:
            return None

        if header.dataType == DataTypes.NONE:
            header = self.lastHeader

        self.lastHeader = header

        while True:
            read = min(header.bodyLength - msgLen, self.chunkSize)
            msg.append(self.stream.read(read))

            msgLen += read
            if msgLen >= header.bodyLength:
                break

            self.lastHeader = Header.decode(self.stream)
            if header.timestamp >= 0x00ffffff:
                self.stream.read_ulong()

        body = pyamf.util.BufferedByteStream(''.join(msg))

        out = {'msg': header.dataType}

        if out['msg'] == DataTypes.USER_CONTROL:
            out['eventType'] = body.read_ulong()
            out['eventData'] = body.read()

        elif out['msg'] == DataTypes.WINDOW_ACK_SIZE:
            out['windowAckSize'] = body.read_ulong()

        elif out['msg'] == DataTypes.SET_PEER_BANDWIDTH:
            out['windowAckSize'] = body.read_ulong()
            out['limit'] = body.read_uchar()

        elif out['msg'] == DataTypes.COMMAND:
            decoder = pyamf.amf0.Decoder(body)
            commands = []
            while not body.at_eof():
                commands.append(decoder.readElement())
            out['cmd'] = commands

        elif out['msg'] == DataTypes.INVOKE:
            commands = []
            body.read_char()
            decoder = pyamf.amf0.Decoder(body)

            while not body.at_eof():
                commands.append(decoder.readElement())
            out['cmd'] = commands

        return out

class DataTypes:
    NONE = -1
    SET_CHUNK_SIZE = 1
    USER_CONTROL = 4
    WINDOW_ACK_SIZE = 5
    SET_PEER_BANDWIDTH = 6
    INVOKE = 17
    SHARED_OBJECT = 19
    COMMAND = 20
