# ai.py


import population
import numpy as np
from random import choice


class AI( object ):

    def __init__( self, grid, score, grapher, exp, height):
        self.height = height
        self.grid = grid
        self.score = score
        self.population = population.Population( )
        self.currentGeneration = 0
        self.currentGenome = 0
        self.grapher = grapher
        self.backupGrid = np.zeros( [ 10, 20 ], dtype=np.uint8 )
        self.backupTile = [ 0, 0, 0 ]
        # ===================================================================== 
        self.state = np.zeros( [ self.height, 10 ], dtype=np.uint8 )
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

        state = []
        for item in self.grid.grid:
            # print(item)
            # input()
            state_count = 0
            while state_count < 20 and item[state_count] == 0:
                state_count += 1
                pass
            state += [20 - state_count]
        """
        state_diff=[]
        for i in range(len(state)-1):
            if state[i+1] > state[i]:
                state_diff.append(1)
            elif state[i+1] < state[i]:
                state_diff.append(-1)
            else:
                state_diff.append(0)
        """
        state_diff=[]
        for i in range(len(state)-1):
            state_diff.append(state[i+1] - state[i])
        # print(state)
        # input()


        # self.state = np.copy( self.grid.grid.transpose()[count:count+self.height] )
        # self.state[self.state > 0] = 1
       
        self.state = state_diff
        # for i in range(len(self.state)):
        #     print(self.state[i])
            # if self.state[i] > 0:
                # self.state[i] = 1
        # print(self.state)
        # input()
        # print(self.state)
        # =====================================================================
        initH = self.grid.lastMaxHeight
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

                newH = self.grid.lastMaxHeight

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
                reward, gameover = self.getReward(initH, newH)
                # a = tuple(1,2,3)
                # print(a)
                # print(tile.identifier)
                # input()
                # key = tuple(self.state.flatten().tolist()+[tile.identifier, move, rotate])
                key = tuple(self.state+[tile.identifier, move, rotate])
                # print(key)
                # input()
                
                # nextState = np.copy( self.grid.grid.transpose()[count:count+self.height])
                # nextState[nextState > 0] = 1

                state = []
                for item in self.grid.grid:
                    # print(item)
                    # input()
                    state_count = 0
                    while state_count < 20 and item[state_count] == 0:
                        state_count += 1
                        pass
                    state += [20 - state_count]
                #nextState = state + [tile.identifier]
                """
                state_diff=[]
                for i in range(len(state)-1):
                    if state[i+1] > state[i]:
                        state_diff.append(1)
                    elif state[i+1] < state[i]:
                        state_diff.append(-1)
                    else:
                        state_diff.append(0)
                """
                state_diff=[]
                for i in range(len(state)-1):
                    state_diff.append(state[i+1] - state[i])
                nextState = state_diff + [tile.identifier]
                
                if key not in self.exp:
                    Q = alpha * reward
                    self.exp[key] = (reward, nextState, Q)
                    print("new %f, %f, %f" % (Q, move, rotate))
                elif key in self.exp:
                    Q = self.exp[key][2]
                    Q += alpha * (reward + gamma * self.getMaxQ(nextState, alpha, reward)[0] - Q)
                    self.exp[key] = (reward, nextState, Q)
                    print("old %f, %f, %f" % (Q, move, rotate))

                print(self.state)
                print(state_diff)
                print(reward)
                print(Q)
                input()
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
        # print(self.state.flatten().tolist())
        # Q = self.getMaxQ(self.state.flatten().tolist(), alpha, reward)[0]
        # print(Q)
        # bestAction = self.getMaxQ(self.state.flatten().tolist(), alpha, reward)[1]
        bestAction = self.getMaxQ(self.state, alpha, reward)[1]
        # print(bestAction)
        # input()
        # print(self.getMaxQ(self.state.flatten().tolist()))
        # input()
        bestMove, bestRotate = bestAction[0], bestAction[1]
        # print(bestAction)
        # input()
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
    def getMaxQ( self , nextState, alpha, reward):
        maxQ = -1000000
        best_set = []
        bestAction=()
        found = False
        for k in self.exp:
            # print(k[:-2])
            # print("\n")
            # print(nextState)
            # input()
            equal = 0
            for a, b in zip(k[:-2], nextState):
                if a != b:
                    equal = 0
                    break
                equal = 1
            if equal:
                found = True
                if self.exp[k][2] > maxQ:
                    maxQ = self.exp[k][2]
                    best_set = [k[-2:]]
                    # bestAction = k[-2:]
                    # print("> %f" % maxQ)
                elif self.exp[k][2] == maxQ:
                    best_set += [k[-2:]]
                    # print("== %f" % maxQ)
        if not found:
            maxQ = 0
            bestAction = (np.random.random_integers( -5, 5 ), np.random.random_integers( 0, 2 ))
            # R = self.getReward
                # self.exp[tuple(nextState +[bestAction[0], bestAction[1]])] = (reward, )
                    # print("< %f" % maxQ)
        # print(self.exp[k][2], maxQ)
        # input()
        if len(best_set) > 1:
            bestAction = choice(best_set)
        elif len(best_set) == 1:
            bestAction = best_set[0]
        return maxQ, bestAction

    def getReward( self, h1, h2):
        gameover = False
        if self.grid.checkForGameOver( ):
            gameover = True
        reward = 0
        print('new H: %d, cur H: %d' % (h2, h1))
        reward += (-100) * (h2-h1)
        # reward += self.grid.lastRowsCleared * 4.760666
        # reward += self.grid.lastMaxHeight * -1.510066
        # reward += self.grid.lastSumHeight * 0.0
        # reward += self.grid.lastRelativeHeight * -1.0
        # # reward += self.grid.lastAmountHoles * -0.35663
        # reward += self.grid.lastAmountHoles * -5.35663
        # reward += self.grid.lastRoughness * -0.184483
        reward += self.grid.lastRowsCleared * 500
        # reward += self.grid.lastMaxHeight * -5
        # reward += self.grid.lastSumHeight * -1
        # reward += self.grid.lastRelativeHeight * -1
        # reward += self.grid.lastAmountHoles * -1
        # reward += self.grid.lastRoughness * -1
        #reward += gameover * (-500)
        return reward, gameover
    # =====================================================================
