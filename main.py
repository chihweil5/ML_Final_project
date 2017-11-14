# main.py


import timeController
import scoreController
import gridController
import tileController

import grapher

import ai

import viewController


timeController = timeController.TimeController( 1 )
scoreController = scoreController.ScoreController( )
gridController = gridController.GridController( scoreController )
tileController = tileController.TileController( gridController )

grapher = grapher.Grapher( scoreController )

ai = ai.AI( gridController, scoreController, grapher, {}, 20)

viewController = viewController.ViewController( gridController, timeController, scoreController, ai, grapher )

index = 0

# =====================================================================
cTile = tileController.getTile( index )
index += 1
nTile = tileController.getTile( index )
# =====================================================================


# cTile = tileController.getRandomTile( )
# nTile = tileController.getRandomTile( )
viewController.setTile( cTile, nTile )


while not viewController.abort:
    if timeController.timeEvent( ):
        if viewController.aiState:
            #move, rotate, rating =  ai.makeMove( cTile )
            ai.train(cTile)
        if not cTile.incY( ):
            cTile.apply( )

            if not gridController.checkForGameOver( ):
                scoreController.tileReleased( )
                cTile = nTile
                index += 1
                nTile = tileController.getTile( index )
                viewController.setTile( cTile, nTile )
            else:
                index = 0
                cTile = tileController.getTile( index )
                index += 1
                nTile = tileController.getTile( index )
                viewController.setTile( cTile, nTile )
    viewController.updateEverything( )
