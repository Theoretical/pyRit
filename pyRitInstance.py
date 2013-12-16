def ClientInstance(client, socket):
    """
    This should only be invoked by pyRit as it's our RTMP instance in a separate process.
    This method is to allow us to have concurrent connections to the Riot Games RTMP server.

    @type client: LolClient
    @type socket: Pipe
    """

    # Little fallback for our operations from pyRit, just to be sure that our callback is implemented.
    def fallback(args):
        return 'Operation not implemented!'

    client.connect()

    while True:
        try:
            operation,args = socket.recv()
        except EOFError:
            continue

        print 'Received operation: {0} | Args: {1}'.format(operation, args)

        operations = {
            'name': client.getSummonerService().getSummonerByName,
            'recent': client.getPlayerStatsService().getRecentGames,
            'game': client.getGameService().retrieveInProgressSpectatorGameInfo,
            'stats': client.getPlayerStatsService().getAggregatedStats,
            'leagues': client.getLeaguesServiceProxy().getLeagueForPlayer,
        }

        socket.send(operations.get(operation, fallback)(args))

