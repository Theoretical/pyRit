import time
import uuid
from pyamf import amf0, TypedObject

class AmfEncoder:
    def __init__(self):
        self.startTime = 0

    def _addHeaders(self, data):
        headers = bytearray()

        # header
        headers.append(3)

        #time stamp
        timestamp = int(round(time.time() * 1000))
        timeDifference = timestamp - self.startTime

        headers.append((timeDifference & 0xFF0000) >> 16)
        headers.append((timeDifference & 0x00FF00) >> 8)
        headers.append((timeDifference & 0x0000FF))

        #body length
        dataLength = len(data)
        headers.append((dataLength & 0xFF0000) >> 16)
        headers.append((dataLength & 0x00FF00) >> 8)
        headers.append((dataLength & 0x0000FF))

        #content-type
        headers.append(0x11)

        #source
        headers.append(0)
        headers.append(0)
        headers.append(0)
        headers.append(0)

        #body
        for i in range(0, dataLength):
            headers.append(data[i])

            if i % 128 == 127 and i != dataLength - 1:
                headers.append(0xC3)

        return headers

    def encodeConnect(self, params):
        self.startTime = int(round(time.time() * 1000))
        encoder = amf0.Encoder()
        encoder.writeString('connect')
        encoder.writeNumber(1)
        encoder.writeAMF3(params)

        encoder.writeBoolean(False)
        encoder.writeString('nil')
        encoder.writeString('')

        to = TypedObject('flex.messaging.messages.CommandMessage')
        to['messageRefType'] = None
        to['operation'] = 5
        to['correlationId'] = ''
        to['clientId'] = None
        to['destination'] = ''
        to['messageId'] = str(uuid.uuid4())
        to['timestamp'] = 0
        to['timeToLive'] = 0
        to['body'] = TypedObject('')
        to['headers'] = {'DSMessagingVersion': 1, 'DSId': 'my-rtmps'}

        encoder.writeAMF3(to)
        data = self._addHeaders(bytearray(encoder.stream.getvalue()))
        data[7] = 0x14
        return data

    def encodeInvoke(self, invokeId, typedObject):
        encoder = amf0.Encoder()

        encoder.stream.write_uchar(0)
        encoder.writeNull(0)
        encoder.writeNumber(invokeId)
        encoder.writeNull(0)

        encoder.writeAMF3(typedObject)
        return self._addHeaders(bytearray(encoder.stream.getvalue()))

