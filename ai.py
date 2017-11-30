# ai.py


import population
import numpy as np
from random import choice

WIDTH = 6
HEIGHT = 12

class AI( object ):

    def __init__( self, grid, score, grapher, exp, height):
        self.height = height
        self.grid = grid
        self.score = score
        self.population = population.Population( )
        self.currentGeneration = 0
        self.currentGenome = 0
        self.grapher = grapher
        self.backupGrid = np.zeros( [ WIDTH, HEIGHT ], dtype=np.uint8 ) #change width #change height
        self.backupTile = [ 0, 0, 0 ]
        # ===================================================================== 
        # self.state = np.zeros( [ self.height, 10 ], dtype=np.uint8 )
        self.state = np.zeros( [ self.grid.width], dtype=np.uint8 )
        if exp != {}:
            self.exp = exp
        else:
            self.exp = {}    
        self.gamma = 0.9
        self.alpha = 0.02
        # =====================================================================

    # =====================================================================

    def train(self, tile):
        bestMove, bestRotate = self.chooseBestAction(tile)
        self.update(tile, bestMove, bestRotate)

    def update(self, tile, bestMove, bestRotate):
        self.grid.realAction = True
        self.grid.grid = np.copy( self.backupGrid )
        initH = self.grid.lastMaxHeight
        
        self.state = self.calculateState()
        curStateWithTile = self.state + [tile.identifier]
        curStateKey = tuple(curStateWithTile + [bestMove, bestRotate])

        for i in range( 0, bestRotate ):
            tile.rotCW( )
        if bestMove<0:
            for i in range( 0, -bestMove ):
                tile.decX( )
        if bestMove>0:
            for i in range( 0, bestMove ):
                tile.incX( )
        tile.drop( )
        tile.apply( )
        self.grid.removeCompleteRows( )

        newH = self.grid.lastMaxHeight
        nextState = self.calculateState()
        nextStateWithTile = nextState + [tile.identifier]
        nextStateKey = tuple(nextStateWithTile + [bestMove, bestRotate])
        # print(curStateKey)
        # print(nextStateKey)
        # input()
        reward = self.getReward(initH, newH)
        ####UPDATE Q!!!!
        if curStateKey not in self.exp:
            self.exp[curStateKey] = 0
        
        self.exp[curStateKey] = (1 - self.alpha) * self.exp[curStateKey] + self.alpha * (reward + self.gamma * self.exp[nextStateKey])
        # print(curStateKey)
        # print(self.exp[curStateKey])
    
    def chooseBestAction(self, tile):
        self.backupGrid = np.copy( self.grid.grid )
        self.grid.realAction = False
        self.backupTile = [ tile.psX, tile.psY, tile.rot ]
        self.state = self.calculateState()
        fitness_old = self.fitness()

        old = False
        initH = self.grid.lastMaxHeight
        maxQ = float('-inf')
        for move in range( -5, 6 ):
            for rotate in range( 0, 4 ):
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
                fitness_new = self.fitness()
                # reward = self.getReward(initH, newH)
                reward = self.getReward(fitness_old, fitness_new)
                # print(reward)

                nextState = self.calculateState()
                nextStateWithTile = nextState + [tile.identifier]
                nextStateKey = tuple(nextStateWithTile + [move, rotate])
                
                if nextStateKey not in self.exp:
                    old = False
                    self.exp[nextStateKey] = 0
                elif self.exp[nextStateKey] != 0:                    
                    old = True
                    
                Q = self.exp[nextStateKey]
                if (reward + self.gamma * Q) >= maxQ:
                    newQ = self.exp[nextStateKey]
                    maxQ = reward + self.gamma * Q
                    bestMove = move
                    bestRotate = rotate

                # print('next H: %d, cur H: %d' % (newH, initH))
                # print(self.state)
                # print(nextState)
                # print(Q)
                # print(move, rotate)

                tile.psX, tile.psY, tile.rot = self.backupTile
                self.grid.grid = np.copy( self.backupGrid )
        if old:
            print("old %f, %f, %f, %f" % (maxQ, newQ, bestMove, bestMove))
            # input()
        else:
            print("====new==== %f, %f, %f, %f" % (maxQ, newQ, bestMove, bestMove))
        # print('bestAction: (%d, %d)' % (bestMove, bestRotate))
        # print('Max Q:', maxQ)
        #input()
        return bestMove, bestRotate

    def fitness(self):
        #print('next H: %d, cur H: %d' % (h2, h1))
        fitness = 0
        fitness += self.grid.lastRowsCleared * 0.76
        # reward += self.grid.lastMaxHeight * -1.510066
        fitness += self.grid.lastSumHeight / 10 * -0.51
        # reward += self.grid.lastRelativeHeight * -1.0
        fitness += self.grid.lastAmountHoles * -0.36
        fitness += self.grid.lastRoughness * -0.18
        # reward = (-100) * (h2-h1)
        return fitness

    def getReward(self, fitness_old, fitness_new):
        return fitness_new - fitness_old

    def calculateState(self):
        count = 0
        test = [1,1,1,1,1,1] #change width
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
            while state_count < HEIGHT and item[state_count] == 0:
                state_count += 1
                pass
            state += [HEIGHT - state_count]

        state_diff=[]
        for i in range(len(state)-1):
            # state_diff.append(state[i+1] - state[i])
            if state[i+1] - state[i] > 0:
                state_diff.append(1)
            elif state[i+1] - state[i] < 0:
                state_diff.append(-1)
            else:
                state_diff.append(0)

        return state_diff

    """
    def getMaxQ( self , nextState, reward):
        maxQ = -1000000
        best_set = []
        bestAction=()
        found = False
        key_set = []
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
                    key_set.append(k)
                    # bestAction = k[-2:]
                    # print("> %f" % maxQ)
                elif self.exp[k][2] == maxQ:
                    best_set += [k[-2:]]
                    key_set.append(k)
                    # print("== %f" % maxQ)
        if not found:
            maxQ = 0
            bestAction = (np.random.random_integers( -5, 5 ), np.random.random_integers( 0, 2 ))
            key_set.append()
            # R = self.getReward
                # self.exp[tuple(nextState +[bestAction[0], bestAction[1]])] = (reward, )
                    # print("< %f" % maxQ)
        # print(self.exp[k][2], maxQ)
        # input()
        if len(best_set) > 1:
            bestAction = choice(best_set)
            bestKey = choice(key_set)
        elif len(best_set) == 1:
            bestAction = best_set[0]
            bestKey = key_set[0]
        else:
            bestKey = ()

        return bestKey
    
    def getReward( self, h1, h2):
        gameover = False
        if self.grid.checkForGameOver( ):
            gameover = True
        reward = 0
        print('next H: %d, cur H: %d' % (h2, h1))
        reward += (-100) * (h2-h1)
        # reward += self.grid.lastRowsCleared * 4.760666
        # reward += self.grid.lastMaxHeight * -1.510066
        # reward += self.grid.lastSumHeight * 0.0
        # reward += self.grid.lastRelativeHeight * -1.0
        # # reward += self.grid.lastAmountHoles * -0.35663
        # reward += self.grid.lastAmountHoles * -5.35663
        # reward += self.grid.lastRoughness * -0.184483
        #reward += self.grid.lastRowsCleared * 500
        # reward += self.grid.lastMaxHeight * -5
        # reward += self.grid.lastSumHeight * -1
        # reward += self.grid.lastRelativeHeight * -1
        # reward += self.grid.lastAmountHoles * -1
        # reward += self.grid.lastRoughness * -1
        #reward += gameover * (-500)
        return reward, gameover
    """
    # =====================================================================
