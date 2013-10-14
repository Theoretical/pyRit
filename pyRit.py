from rtmp.client import RtmpClient
from flask import Flask, jsonify

app = Flask(__name__)
client = RtmpClient('NA', '', '')


@app.route('/history/<acctId>')
def getRecentGames(acctId):
    msg = None
    invokeId = client.invoke('playerStatsService', 'getRecentGames', [int(float(acctId))], None)

    while msg is None:
        msg = client.getPendingRequest(invokeId)

    return jsonify(msg['cmd'][3].body)


@app.route('/public/<acctId>')
def getAllPublicSummonerDataByAccount(acctId):
    msg = None
    invokeId = client.invoke('summonerService', 'getAllPublicSummonerDataByAccount', [int(float(acctId))], None)

    while msg is None:
        msg = client.getPendingRequest(invokeId)

    return jsonify(msg['cmd'][3].body)

@app.route('/name/<summonerName>')
def getSummonerByName(summonerName):
    msg = None
    invokeId = client.invoke('summonerService', 'getSummonerByName', [summonerName], None)

    while msg is None:
        msg = client.getPendingRequest(invokeId)

    return jsonify(msg['cmd'][3].body)


client.connect()
app.run(host='0.0.0.0')
