-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

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
	ORDER BY wins DESC;