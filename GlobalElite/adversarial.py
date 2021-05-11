# Monte Carlo Search Tree algorithm inspired by Jeff Bradberry from his blog
# http://jeffbradberry.com/posts/2015/09/intro-to-monte-carlo-tree-search/


from collections import defaultdict
from referee.game import play

adjacent = [(1, -1), (1, 0), (0, 1), (-1, 1), (-1, 0), (0, -1)]
upper_throw_left = 9
lower_throw_left = 9

class Player:
    
    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        # put your code here
        self.player = player
        self.board = self.generate_board()
        self.token_on_board = defaultdict(list)
        


    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        # put your code here



        
    
    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        # player move update
        if player_action[0] == "THROW":
            if self.player == "upper":
                self.token_on_board[player_action[2]].append(player_action[1].upper())
                upper_throw_left-=1
            else:
                self.token_on_board[player_action[2]].append(player_action[1])
                lower_throw_left-=1
        else:
            to_be_moved = self.token_on_board[player_action[1]].pop()
            self.token_on_board[player_action[2]].append(to_be_moved)

        # opponent move update
        if opponent_action[0] == "THROW":
            if self.player == "upper":
                self.token_on_board[opponent_action[2]].append(opponent_action[1])
                lower_throw_left-=1
            else:
                self.token_on_board[opponent_action[2]].append(opponent_action[1].upper())
                upper_throw_left-=1
        else:
            to_be_moved = self.token_on_board[opponent_action[1]].pop()
            self.token_on_board[opponent_action[2]].append(to_be_moved)
        
        self.battle([player_action[2], opponent_action[2]])

    def winner(self):
        pass

    # check for available move for one token/location
    # return a dictionary that maps the location to all possible moves
    def available_moves(self, x):
        result = set()
        all_hex = set(self.board.keys())
        
        rx, qx = x
        neighbours = all_hex & {(rx + ry, qx + qy) for ry, qy in adjacent}
        
        for ry,qy in neighbours:
            if self.token_on_board[(ry,qy)]:
                
                if not self.defeat(self.token_on_board[(ry,qy)][0], self.token_on_board[(rx,qx)][0]):
                    result.add((ry,qy))
                
                if self.token_on_board[(ry,qy)][0].isupper() == self.token_on_board[(rx,qx)].isupper():
                    swing_hex = all_hex & {(ry + rz, qy + qz) for rz, qz in adjacent}
                    swing_hex.remove((rx,qx))
                    result = result | swing_hex
        
        return {x:result}
    
    # check if x can defeat y
    def defeat(self,x,y):
        rule = {"r":"s","s":"p","p":"r"}
        return rule[x.lower()] == y.lower()
    
    # handle battle stage after both player has finished their move
    def battle(self, change):
        for coord in change:
            
            current_hex = self.token_on_board[coord]
            
            if len(current_hex) > 1:

                string = "".join(current_hex)
                string.lower()

                # all is defeated if the hex contains all three types of token
                if "r" in string and "p" in string and "s" in string:
                    self.token_on_board[coord].clear()
                
                else:
                    for i in current_hex:
                        for j in current_hex:
                            if self.defeat(i,j):
                                self.token_on_board[coord] = list(filter(lambda a: a != j, current_hex))
                            elif self.defeat(j,i):
                                self.token_on_board[coord] = list(filter(lambda a: a != i, current_hex))

    # generate a board for the game
    def generate_board(self):
        board = defaultdict(list)
        ran = range(-3, 4)
        for r,q in [(r,q) for r in ran for q in ran if -r-q in ran]:
            board[(r,q)].append((r,q+1))
            board[(r,q)].append((r,q-1))
            board[(r,q)].append((r+1,q))
            board[(r,q)].append((r-1,q))
            board[(r,q)].append((r+1,q-1))
            board[(r,q)].append((r-1,q+1))
        
        board[(4,-4)].append((3,-4))
        board[(4,-4)].append((4,-3))
        board[(4,-4)].append((3,-3))

        board[(4,-3)].append((4,-4))
        board[(4,-3)].append((4,-2))
        board[(4,-3)].append((3,-3))
        board[(4,-3)].append((3,-2))

        board[(4,-2)].append((4,-3))
        board[(4,-2)].append((4,-2))
        board[(4,-2)].append((3,-2))
        board[(4,-2)].append((3,-1))

        board[(4,-1)].append((4,-2))
        board[(4,-1)].append((4,0))
        board[(4,-1)].append((3,-1))
        board[(4,-1)].append((3,0))

        board[(4,0)].append((4,-1))
        board[(4,0)].append((3,0))
        board[(4,0)].append((3,1))


        board[(3,-4)].append((4,-4))
        board[(3,-4)].append((3,-3))
        board[(3,-4)].append((2,-4))
        board[(3,-4)].append((2,-3))

        board[(2,-4)].append((3,-4))
        board[(2,-4)].append((2,-3))
        board[(2,-4)].append((1,-4))
        board[(2,-4)].append((1,-3))

        board[(1,-4)].append((2,-4))
        board[(1,-4)].append((1,-3))
        board[(1,-4)].append((0,-4))
        board[(1,-4)].append((0,-3))

        board[(0,-4)].append((1,-4))
        board[(0,-4)].append((0,-3))
        board[(0,-4)].append((-1,-3))

        board[(-1,-3)].append((0,-4))
        board[(-1,-3)].append((0,-3))
        board[(-1,-3)].append((-1,-2))
        board[(-1,-3)].append((-2,-2))

        board[(-2,-2)].append((-1,-3))
        board[(-2,-2)].append((-1,-2))
        board[(-2,-2)].append((-2,-1))
        board[(-2,-2)].append((-3,-1))

        board[(-3,-1)].append((-2,-2))
        board[(-3,-1)].append((-2,-1))
        board[(-3,-1)].append((-3,0))
        board[(-3,-1)].append((-4,0))

        board[(-4,0)].append((-3,-1))
        board[(-4,0)].append((-3,0))
        board[(-4,0)].append((-4,1))

        board[(-4,1)].append((-4,0))
        board[(-4,1)].append((-4,2))
        board[(-4,1)].append((-3,0))
        board[(-4,1)].append((-3,1))

        board[(-4,2)].append((-4,1))
        board[(-4,2)].append((-4,3))
        board[(-4,2)].append((-3,1))
        board[(-4,2)].append((-3,2))

        board[(-4,3)].append((-4,2))
        board[(-4,3)].append((-4,4))
        board[(-4,3)].append((-3,2))
        board[(-4,3)].append((-3,3))

        board[(-4,4)].append((-4,3))
        board[(-4,4)].append((-3,3))
        board[(-4,4)].append((-3,4))

        board[(-3,4)].append((-4,4))
        board[(-3,4)].append((-3,3))
        board[(-3,4)].append((-2,3))
        board[(-3,4)].append((-2,4))

        board[(-2,4)].append((-3,4))
        board[(-2,4)].append((-2,3))
        board[(-2,4)].append((-1,3))
        board[(-2,4)].append((-1,4))

        board[(-1,4)].append((-2,4))
        board[(-1,4)].append((-1,3))
        board[(-1,4)].append((0,3))
        board[(-1,4)].append((0,4))

        board[(0,4)].append((-1,4))
        board[(0,4)].append((0,3))
        board[(0,4)].append((1,3))
        
        board[(1,3)].append((0,4))
        board[(1,3)].append((0,3))
        board[(1,3)].append((1,2))
        board[(1,3)].append((2,2))

        board[(2,2)].append((1,3))
        board[(2,2)].append((1,2))
        board[(2,2)].append((2,1))
        board[(2,2)].append((3,1))

        board[(3,1)].append((2,2))
        board[(3,1)].append((2,1))
        board[(3,1)].append((3,0))
        board[(3,1)].append((4,0))

        return board
