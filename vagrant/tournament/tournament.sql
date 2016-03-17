-- Table, view, and function definitions for the tournament project.

DROP DATABASE IF EXISTS tournament;

CREATE DATABASE tournament;

\c tournament;

CREATE TABLE IF NOT EXISTS players (
    id			serial PRIMARY KEY,
    name		varchar(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS matches (
    winner    		integer references players(id),
    loser    		integer references players(id)
);

CREATE VIEW standings AS
	SELECT p.id id, p.name player,
	(SELECT count(*) FROM matches m WHERE p.id = m.winner) wins,
	(SELECT count(*) FROM matches m WHERE p.id = m.winner OR p.id = m.loser) matches
	FROM players p
	ORDER BY wins DESC,
			 matches ASC;
	
-- Creates a function that validates a player id
-- returns:
-- true:  valid player id
-- false: invalid player id
CREATE FUNCTION checkplayer(integer) RETURNS boolean 
	AS $$
	SELECT count(*) > 0 
	FROM players 
	WHERE id = $1
	$$
    LANGUAGE SQL;
    
-- Creates a function that takes 2 players by players.id and checks if they have played 
-- each other before by checking the matches table.
-- returns:
-- true:  they have played before
-- false: they have NOT played before
CREATE FUNCTION checkpairing(integer, integer) RETURNS boolean 
	AS $$
	SELECT count(*) > 0 
	FROM matches 
	WHERE (winner = $1 AND loser = $2) OR (winner = $2 AND loser = $1)
	$$
    LANGUAGE SQL;
    
