from coordinates import Coordinate
import random
import sys
import numpy as np
from numpy.random import randn


if sys.version_info >= (3,):
    xrange = range

    
class Player(object):
    def __init__(self):
        self.vision = None
        self.genome = None

    def take_turn(self, genome, vision):
        self.vision = vision
        self.genome = genome
        return self.turn()

    def bit_at(self, position):
        return (self.genome >> position) & 1

    def bit_range(self, start, stop):
        return (self.genome >> start) & ((1 << (stop-start)) - 1)

    def bit_chunk(self, start, length):
        return (self.genome >> start) & ((1 << length) - 1)

    def turn(self):
        return Coordinate(1, 0)

    def vision_at(self, x, y):
        return self.vision[2+y][2+x]


class ForwardPlayer(Player):
    def turn(self):
        return Coordinate(1, 0)


class RandomPlayer(Player):
    def turn(self):
        return Coordinate(1, random.randint(-1, 1))


class LinearCombinationPlayer(Player):
    def __init__(self):
        Player.__init__(self)
        self.coords = [#Coordinate(-1,-1),
                       #Coordinate( 0,-1),
                       Coordinate( 1, 0),
                       Coordinate( 1,-1),
                       #Coordinate(-1, 0),
                       #Coordinate( 0, 0),
                       #Coordinate(-1, 1),
                       #Coordinate( 0, 1),
                       Coordinate( 1, 1)]
        self.n_moves = len(self.coords)

    def turn(self):
        restricted_coords = [c for c in self.coords if self.vision_at(c.x,c.y)>-1]
        restricted_n_moves = len(restricted_coords)
        s = 0
        for i in range(25):
            s += self.bit_range(2*i,2*i+2)*self.vision_at(int(i/5)-2, i%5-2)
        return restricted_coords[s%restricted_n_moves]


class ColorScorePlayer(Player):
    def __init__(self):
        Player.__init__(self)
        self.coords = [#Coordinate(-1,-1),
                       #Coordinate( 0,-1),
                       Coordinate( 1, 0),
                       Coordinate( 1,-1),
                       #Coordinate(-1, 0),
                       #Coordinate( 0, 0),
                       #Coordinate(-1, 1),
                       #Coordinate( 0, 1),
                       Coordinate( 1, 1)]
        self.n_moves = len(self.coords)

    def turn(self):
        max_score = max([self.bit_chunk(6*self.vision_at(c.x, c.y), 6) for c in self.coords if self.vision_at(c.x, c.y)>=0])
        restricted_coords = [c for c in self.coords if self.vision_at(c.x, c.y)>=0 and self.bit_chunk(6*self.vision_at(c.x,c.y), 6) == max_score]

        return random.choice(restricted_coords)


class LemmingPlayer(Player):
    def __init__(self):
        Player.__init__(self)
        self.coords = [Coordinate(-1,-1),
                       #Coordinate( 0,-1),
                       Coordinate( 1, 0),
                       #Coordinate( 1,-1),
                       Coordinate(-1, 0),
                       #Coordinate( 0, 0),
                       Coordinate(-1, 1),
                       #Coordinate( 0, 1),
                       #Coordinate( 1, 1)
                       ]

    def turn(self):
        return random.choice(self.coords)


class IllegalPlayer(Player):
    def __init__(self):
        Player.__init__(self)
        self.coords = [Coordinate(2,-1),
                       Coordinate(2, 0),
                       Coordinate(2, 1)
                       ]
                   
    def turn(self):
        return random.choice(self.coords)

class DistributedColorScorePlayer(Player):
    def __init__(self):
        Player.__init__(self)
        self.coords = [#Coordinate(-1,-1),
                       #Coordinate( 0,-1),
                       Coordinate( 1, 0),
                       #Coordinate( 1,-1),
                       Coordinate(-1, 0),
                       #Coordinate( 0, 0),
                       Coordinate(-1, 1),
                       Coordinate( 0, 1),
                       Coordinate( 1, 1)
                       ]
        dims_to_use = 100
        self.reducer = randn(16, dims_to_use)
        self.reducer -= np.tile(np.mean(self.reducer, axis=1).reshape((16,1)), (1, dims_to_use))

    def turn(self):
        genome_bits = np.array([self.bit_at(i) for i in range(100)])
        color_scores = self.reducer.dot(genome_bits)
        max_score = max([color_scores[self.vision_at(c.x, c.y)] for c in self.coords if self.vision_at(c.x, c.y)>=0])
        restricted_coords = [c for c in self.coords if self.vision_at(c.x, c.y)>=0 and color_scores[self.vision_at(c.x,c.y)] == max_score]

        return random.choice(restricted_coords)


        

PLAYER_TYPE = DistributedColorScorePlayer
