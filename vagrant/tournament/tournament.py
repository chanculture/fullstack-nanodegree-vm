#!/usr/bin/env python
# 
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
import bleach


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
    #print(result)
    return result


def registerPlayer(name):
    """Adds a player to the tournament database.
  
    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)
  
    Args:
      name: the player's full name (need not be unique).
    """
    name = bleach.clean(name)
    conn = connect()
    cur = conn.cursor()
    sql = "INSERT INTO players (name) VALUES (%s)"
    data = (name, )
    cur.execute(sql, data) 
    conn.commit()
    cur.close()
    conn.close()


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

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
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
    # This will only work for even numbers
    for count in range(0, cur.rowcount/2):
        player1 = cur.fetchone()
        player2 = cur.fetchone()
        tupl = (player1[0], player1[1], player2[0], player2[1])
        print(tupl)
        result.append(tupl)
    conn.commit()
    cur.close()
    conn.close()
    return result

