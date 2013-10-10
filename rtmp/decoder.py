import pyamf
import ssl
import pyamf.util.pure
from pyamf import amf0, amf3
from rtmp import defs


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

    def __iter__(self):
        return self

    def next(self):
        if self.stream.at_eof():
            return StopIteration

        msg = []
        msgLen = 0
        try:
            header = defs.Header.decode(self.stream)
        except:
            return -1

        if header.datatype == defs.DataTypes.NONE:
            header = self.lastHeader

        self.lastHeader = header

        while True:
            read = min(header.bodyLength - msgLen, self.chunkSize)
            msg.append(self.stream.read(read))

            msgLen += read
            if msgLen >= header.bodyLength:
                break

            nextHeader = defs.Header.decode(self.stream)
            if header.timestamp >= 0x00ffffff:
                self.stream.read_ulong()

        body = pyamf.util.BufferedByteStream(''.join(msg))

        out = {'msg': header.datatype}

        if out['msg'] == defs.DataTypes.USER_CONTROL:
            out['eventType'] = body.read_ulong()
            out['eventData'] = body.read()
        elif out['msg'] == defs.DataTypes.WINDOW_ACK_SIZE:
            out['windowAckSize'] = body.read_ulong()
        elif out['msg'] == defs.DataTypes.SET_PEER_BANDWIDTH:
            out['windowAckSize'] = body.read_ulong()
            out['limit'] = body.read_uchar()
        elif out['msg'] == defs.DataTypes.COMMAND:
            decoder = pyamf.amf0.Decoder(body)
            commands = []
            while not body.at_eof():
                commands.append(decoder.readElement())
            out['cmd'] = commands
        elif out['msg'] == defs.DataTypes.INVOKE:
            commands = []
            body.read_char()
            decoder = pyamf.amf0.Decoder(body)

            while not body.at_eof():
                commands.append(decoder.readElement())
            out['cmd'] = commands

        return out
