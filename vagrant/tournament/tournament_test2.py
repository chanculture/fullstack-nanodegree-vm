#!/usr/bin/env python
#
# Test cases for tournament.py
# These tests are not exhaustive, but they should cover the majority of cases.
#
# If you do add any of the extra credit options, be sure to add/modify these test cases
# as appropriate to account for your module's added functionality.

from tournament import *

def mytest():
    deleteMatches()
    deletePlayers()
    registerPlayer("Luke Skywalker")
    registerPlayer("Princess Luna")
    registerPlayer("Han Solo")
    registerPlayer("Rey")
    registerPlayer("Count Doku")
    registerPlayer("Darth Vader")
    registerPlayer("Anakin Skywalker")
    registerPlayer("Chewbacca")
	
if __name__ == '__main__':
    mytest()
    print("Test 2 finished.")
