# ai.py


import population
import numpy as np
from random import choice


class AI( object ):

    def __init__( self, grid, score, grapher , exp):
        self.grid = grid
        self.score = score
        self.population = population.Population( )
        self.currentGeneration = 0
        self.currentGenome = 0
        self.grapher = grapher
        self.backupGrid = np.zeros( [ 10, 20 ], dtype=np.uint8 )
        self.backupTile = [ 0, 0, 0 ]
        # ===================================================================== 
        self.state = np.zeros( [ 4, 10 ], dtype=np.uint8 )
        if exp != {}:
            self.exp = exp
        else:
            self.exp = {}    
        # =====================================================================

    def makeMove( self, tile ):
        self.backupGrid = np.copy( self.grid.grid )
        self.grid.realAction = False
        self.backupTile = [ tile.psX, tile.psY, tile.rot ]

        # =====================================================================
        count = 0
        test = [1,1,1,1,1,1,1,1,1,1]
        for i in self.backupGrid.transpose():
            if count > 15:
                break
            elif i.T.dot(test) == 0:
                count += 1
            else:
                break

        self.state = np.copy( self.grid.grid.transpose()[count:count+4] )
        # =====================================================================

        bestRating = -10000000000000
        bestMove = 0
        bestRotate = 0

        for move in range( -5, 6 ):
            for rotate in range( 0, 3 ):
                for i in range( 0, rotate ):
                    tile.rotCW( )
                if move<0:
                    for i in range( 0, -move ):
                        tile.decX( )
                if move>0:
                    for i in range( 0, move ):
                        tile.incX( )
                tile.drop( )
                tile.apply( )
                self.grid.removeCompleteRows( )

                # if self.rateMove( )[ 0 ] > bestRating:
                #     bestMove = move
                #     bestRotate = rotate
                #     bestRating, gameover = self.rateMove( )

                # =====================================================================
                count = 0
                for i in self.grid.grid.transpose():
                    if count > 15:
                        break
                    elif i.T.dot(test) == 0:
                        count += 1
                    else:
                        break
                alpha = 0.2
                gamma = 0.9
                reward, gameover = self.getReward()
                # a = tuple(1,2,3)
                # print(a)

                key = tuple(self.state.flatten().tolist()+[move, rotate])
                # print(key)
                # input()
                nextState = np.copy( self.grid.grid.transpose()[count:count+4]).flatten().tolist()
                if key not in self.exp:
                    Q = alpha * reward
                    self.exp[key] = (reward, nextState, Q)
                else:
                    Q = self.exp[key][2]
                    Q += alpha * (reward + gamma * self.getMaxQ(nextState)[0] - Q)
                    self.exp[key] = (reward, nextState, Q)
                # print(move, rotate, Q)
                # input()
                # print(Q)
                # self.state = np.copy( self.grid.grid.transpose()[count:count+4] )
                # print("%f, %f \n" % (move, rotate))
                # print(self.state)
                # input()
                # =====================================================================

                tile.psX, tile.psY, tile.rot = self.backupTile
                self.grid.grid = np.copy( self.backupGrid )
        # =====================================================================
        bestAction = self.getMaxQ(self.state.flatten().tolist())[1]

        # print(self.getMaxQ(self.state.flatten().tolist()))
        # input()
        bestMove, bestRotate = bestAction[0], bestAction[1]
        # =====================================================================
        
        self.grid.realAction = True
        self.grid.grid = np.copy( self.backupGrid )

        if gameover:
            self.population.generations[ self.currentGeneration ].genomes[ self.currentGenome ].score = self.score.getScore( )
            if self.currentGenome == 39:
                self.grapher.appendDataSet( [ x.score for x in self.population.generations[ self.currentGeneration ].genomes ] )
                self.currentGenome = 0
                self.population.nextGen( )
                self.currentGeneration += 1
            else:
                self.currentGenome += 1

        for i in range( 0, bestRotate ):
            tile.rotCW( )
        if bestMove<0:
            for i in range( 0, -bestMove ):
                tile.decX( )
        if bestMove>0:
            for i in range( 0, bestMove ):
                tile.incX( )
        tile.drop( )

        
        # print(bestMove, bestRotate)

        return bestMove, bestRotate, bestRating

    def rateMove( self ):
        gameover = False
        cGenome = self.population.generations[ self.currentGeneration ].genomes[ self.currentGenome ]
        rating = 0
        rating += self.grid.lastRowsCleared * cGenome.weightRowsCleared
        rating += self.grid.lastMaxHeight * cGenome.weightMaxHeight
        rating += self.grid.lastSumHeight * cGenome.weightSumHeight
        rating += self.grid.lastRelativeHeight * cGenome.weightRelativeHeight
        rating += self.grid.lastAmountHoles * cGenome.weightAmountHoles
        rating += self.grid.lastRoughness * cGenome.weightRoughness
        if self.grid.checkForGameOver( ):
            rating -= 500
            gameover = True
        return rating, gameover

    # =====================================================================
    def getMaxQ( self , nextState):
        maxQ = -100000
        best_set = []
        bestAction=()
        for k in self.exp:
            # print(k[:-2])
            # print("\n")
            # print(nextState)
            # input()
            equal = 0
            for a, b in zip(k[:-2], nextState):
                if a != b:
                    break
                equal = 1
            if equal:
                if self.exp[k][2] > maxQ:
                    maxQ = self.exp[k][2]
                    best_set += [k[-2:]]
                elif self.exp[k][2] == maxQ:
                    best_set += [k[-2:]]
        # print(self.exp[k][2], maxQ)
        # input()
        if len(best_set) > 1:
            bestAction = choice(best_set)
        elif len(best_set) == 1:
            bestAction = best_set[0]
        return maxQ, bestAction

    def getReward( self ):
        gameover = False
        if self.grid.checkForGameOver( ):
            gameover = True
        reward = 0
        reward += self.grid.lastRowsCleared * 0.760666
        reward += self.grid.lastMaxHeight * -0.510066
        reward += self.grid.lastSumHeight * 0.0
        reward += self.grid.lastRelativeHeight * (-0.0)
        reward += self.grid.lastAmountHoles * -0.35663
        reward += self.grid.lastRoughness * -0.184483
        reward += gameover * (-500)
        return reward, gameover
    # =====================================================================
