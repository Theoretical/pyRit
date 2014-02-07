from swf.movie import SWF
from urllib2 import urlopen, HTTPError


def fetch_current_version():
    request = urlopen('http://l3cdn.riotgames.com/releases/live/projects/lol_air_client/releases/releaselisting')
    versions = request.read().split('\n')
    url = 'http://l3cdn.riotgames.com/releases/live/projects/lol_air_client/releases/{0}/files/lib/ClientLibCommon.dat'

    for index in range(1, len(versions)):
        version = versions[index].replace('\b', '').replace('\r', '')

        try:
            request = urlopen(url.format(version))
            open('ClientLibCommon.dat', 'wb').write(request.read())
            break
        except HTTPError:
            continue

    f = open('ClientLibCommon.dat', 'rb')
    swf = SWF(f)
    for tag in swf.tags:
        if tag.TYPE == 82 and 'Version' in tag.abcName:
            start = 'CURRENT_VERSION'
            end = 'String'
            data = tag.bytes
            return data[data.index(start) + len(start):data.index(end)]
