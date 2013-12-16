def ClientInstance(client, socket):
    """
    This should only be invoked by pyRit as it's our RTMP instance in a separate process.
    This method is to allow us to have concurrent connections to the Riot Games RTMP server.

    @type client: LolClient
    @type socket: Pipe
    """

    client.connect()

    while True:
        msg = socket.recv()

        # Thanks to broken for this amazing formatting and more pythony implementation! :)
        operation = msg[0]
        args = msg[1]

        def fallback():
            return "Operation not implemented!"

        operations = {
            'name': client.getSummonerService().getSummonerByName,
            'recent': client.getPlayerStatsService().getRecentGames,
            'game': client.getGameService().retrieveInProgressSpectatorGameInfo,
            'stats': client.getPlayerStatsService().getAggregatedStats,
            'leagues': client.getLeaguesServiceProxy().getLeagueForPlayer,
            'fallback': fallback,
        }

        socket.send(operations.get(operation, "fallback")(args))

        print msg
