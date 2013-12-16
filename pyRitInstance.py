def ClientInstance(client, socket):
    """
    This should only be invoked by pyRit as it's our RTMP instance in a separate process.
    This method is to allow us to have concurrent connections to the Riot Games RTMP server.

    @type client: LolClient
    @type socket: Pipe
    """

    client.connect()

    while True:
        operation,args = socket.recv()

        print 'Received operation: {0} | Args: {1}'.format(operation, args)

        def fallback(args):
            return 'Operation not implemented!'

        operations = {
            'name': client.getSummonerService().getSummonerByName,
            'recent': client.getPlayerStatsService().getRecentGames,
            'game': client.getGameService().retrieveInProgressSpectatorGameInfo,
            'stats': client.getPlayerStatsService().getAggregatedStats,
            'leagues': client.getLeaguesServiceProxy().getLeagueForPlayer,
            'fallback': fallback,
        }

        socket.send(operations.get(operation, 'fallback')(args))

