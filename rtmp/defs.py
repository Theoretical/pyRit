class Header:
    __slots__ = ('streamId', 'datatype', 'timestamp', 'bodyLength', 'channelId', 'full')

    def __init__(self, channelId, timestamp=-1, datatype=-1,
                 bodyLength=-1, streamId=-1, full=False):
        self.channelId = channelId
        self.timestamp = timestamp
        self.datatype = datatype
        self.bodyLength = bodyLength
        self.streamId = streamId
        self.full = full

    def __repr__(self):
        attrs = []

        for k in self.__slots__:
            v = getattr(self, k, None)

            if v == -1:
                v = None

            attrs.append('%s=%r' % (k, v))

        return '<%s.%s %s at 0x%x>' % (
            self.__class__.__module__,
            self.__class__.__name__,
            ' '.join(attrs),
            id(self))

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
            header.datatype = data.read_uchar()

        if bits < 1:
            data.endian = '<'
            header.streamId = data.read_ulong()
            data.endian = '!'

            header.full = True

        if header.timestamp == 0xffffff:
            header.timestamp = data.read_ulong()

        return header


class DataTypes:
    NONE = -1
    SET_CHUNK_SIZE = 1
    USER_CONTROL = 4
    WINDOW_ACK_SIZE = 5
    SET_PEER_BANDWIDTH = 6
    INVOKE = 17
    SHARED_OBJECT = 19
    COMMAND = 20