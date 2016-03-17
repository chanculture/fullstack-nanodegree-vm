Christopher Chan
Full Stack Web Developer Nanodegree

Project 2: Tournament Results
==========
This project aims to create an engine capable of simulating a Swiss tournament with the
use of a Python functions library and a PostgreSQL database.

Requirements
==========

Python 2.7.6 or greater
PostgreSQL 

Documentation
==========
To run this project follow these steps:

Clone the git repository located at: 
https://github.com/chanculture/fullstack-nanodegree-vm

The files necessary for this project are located /vagrant/tournament

1) In the psql CLI, import tournament.sql  "\i tournament.sql"
2) In the Vagrant command line, run tournament_test.py. "python tournament_test.py"

Content
==========

tournament.sql: Contains the instruction set to set up the database necessary to run and 
complete the requirements for this project.  CAUTION: Every time this file is imported, 
it will DROP a database named "tournament" and re-create it.

tournament.py: Contains the functionality behind the completing the project tasks.

tournament_test.py: Contains test unit functions to test the functionality of both the
tournament database and the functionality of tournament.py.  NOTE: this file was altered
from the forked version at https://github.com/udacity/fullstack-nanodegree-vm to reflect
print function syntax.

tournament_test2.py: This file can be ignored, it was used and modified for my own testing
as opposed to creating heavy modification to tournament_test.py

License
==========
Copyright Christopher Chan