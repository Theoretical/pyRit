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

        operation = msg[0]
        args = msg[1]

        if  operation == 'name':
            summoner = client.getSummonerService().getSummonerByName(args[0])
            socket.send(summoner)

        elif operation == 'recent':
            recent = client.getPlayerStatsService().getRecentGames(args[0])
            socket.send(recent)

        elif operation == 'game':
            gameInProgress = client.getGameService().retrieveInProgressSpectatorGameInfo(args[0])
            socket.send(gameInProgress)

        elif operation == 'stats':
            stats = client.getPlayerStatsService().getAggregatedStats(args[0], args[1])
            socket.send(stats)

        elif operation == 'leagues':
            leagues = client.getLeaguesServiceProxy().getLeagueForPlayer(args[0])
            socket.send(leagues)

        print msg
