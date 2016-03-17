#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach
from collections import deque


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")

def closeConnection( conn ):
    conn.close()

def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE from matches")
    conn.commit()
    cur.close()
    conn.close()

def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE from players")
    conn.commit()
    cur.close()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT count(*) as num FROM players")
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    #Sanitize data for insertion
    name = bleach.clean(name)
    
    conn = connect()
    cur = conn.cursor()
    sql = "INSERT INTO players (name) VALUES (%s)"
    data = (name, )
    cur.execute(sql, data) 
    conn.commit()
    cur.close()
    conn.close()

def isPlayerById(iden):
    # Sanitize data for insertion.
    iden = bleach.clean(iden)
    
    conn = connect()
    cur = conn.cursor()
    sql = "SELECT * FROM checkplayer(%s)"
    data = (iden, )
    cur.execute(sql, data)
    result = cur.fetchone()[0]
    return result


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM standings")
    result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return result

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Prevents the reporting of two players that have have already played each other during the
    course of the tournament.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    #Sanitize data for insertion
    winner = bleach.clean(winner)
    loser = bleach.clean(loser)

    if checkPairing(winner, loser):
        raise ValueError("This pairing of players has already been matched during this tournament")
    
    conn = connect()
    cur = conn.cursor()
    sql = "INSERT INTO matches (winner, loser) VALUES (%s, %s)"
    data = (winner, loser, )
    cur.execute(sql, data) 
    conn.commit()
    cur.close()
    conn.close()
 
def swissPairings():
    """Returns a list of pairs of players for the next round of a match.
  
    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    EXTRA CREDIT:
    This function prevents the same pair from playing each other more than once in
    a tournamet.

    Method:
    1) iterate through the view "standings", starting with player1 = row1
    2) try to pair player1 with their immediate adjacent player (player2)
    3) if they have already been been paired before, add player2 to a queue
    4) repeat 2) and 3) until a player who has not been paired with player1 is found
    5) grab players from the queue before iterating further through "standings" in
       order to populate new player1 and player2 objects
       
  
    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM standings")
    result = []

    # declare player1, player2 as variables for use
    player1 = None
    player2 = None
    # define empty queue for use
    queue = deque([])
    row = cur.fetchone()
    # iterate the database cursor until we reach the end.
    while row is not None:
        #populate player1
        if player1 is None:
            if len(queue) == 0:
                player1 = row
            else:
                player1 = queue.popleft()
        #populate player2
        if player2 is None:
            if len(queue) > 0:
                player2 = queue.popleft()
            elif player1 != row:
                player2 = row
            else:
                player2 = cur.fetchone()
        
        if not checkPairing(player1[0], player2[0]):
            # valid pairing found
            tupl = (player1[0], player1[1], player2[0], player2[1])
            result.append(tupl)
            player1 = None
            player2 = None
            row = cur.fetchone()
        else:
            # invalid pairing, add player2 to queue, and get the next value in "standings"
            queue.append(player2)
            player2 = cur.fetchone()
          
    conn.commit()
    cur.close()
    conn.close()
    #print(result)
    return result

def checkPairing(player1, player2):
    """Returns true or false, whether player1 has already played player2 in the tournament

    player1 and player2 should be two different, valid players in the database.

    Returns:
      True: players have already played against each other.
      False: players have not already played against each other or player1 and player2 are
      identical or invalid.
    """
    # Sanitize data for insertion.
    # This is done here for future use; so that this function can be called standalone
    player1 = bleach.clean(player1)
    player2 = bleach.clean(player2)

    # returns false if the same player is passed to the function
    if player1 == player2:
        return False
    # returns false if either player is not a valid player.id
    if not isPlayerById(player1):
        return False
    if not isPlayerById(player2):
        return False
    
    conn = connect()
    cur = conn.cursor()
    sql = "SELECT * FROM checkpairing(%s,%s)"
    data = (player1, player2, )
    cur.execute(sql, data)
    result = cur.fetchone()[0]
    return result

