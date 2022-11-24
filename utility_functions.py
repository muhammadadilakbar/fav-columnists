"""
Some utility functions
"""

def createList( listOfDicts, id ):
    """
    Takes a list of dictionaries and returns a list containing column identification numbers
    """
    list = []
    for d in listOfDicts:
        list.append( d[ id ] )
    return list