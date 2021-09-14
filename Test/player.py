from Test import player
from collections import defaultdict
from referee.game import play
from random import choice

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
        self.upper_throw_left = 9
        self.lower_throw_left = 9
        

        


    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        # put your code here
        moves = []
        print(self.token_on_board.items())
        if self.player == "lower" and self.lower_throw_left > 0:
            area = 5-self.lower_throw_left
            for location in self.board:
                if location[0] <= area:
                    moves.append(("THROW", "r", location))
                    moves.append(("THROW", "p", location))
                    moves.append(("THROW", "s", location))
        elif self.player == "upper" and self.upper_throw_left > 0:
            area = self.upper_throw_left-5
            for location in self.board:
                if location[0] >= area:
                    moves.append(("THROW", "r", location))
                    moves.append(("THROW", "p", location))
                    moves.append(("THROW", "s", location))

        if self.token_on_board:
            for i in self.token_on_board:
                if self.token_on_board[i]:
                    for token in self.token_on_board[i]:
                        if token.islower() and self.player == "lower":
                            for each in self.available_moves(i):
                                moves.append(each)
                        elif token.isupper() and self.player == "upper":
                            for each in self.available_moves(i):
                                moves.append(each)
        
        return choice(moves)



        
    
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
                self.upper_throw_left-=1
            else:
                self.token_on_board[player_action[2]].append(player_action[1])
                self.lower_throw_left-=1
        else:
            if self.player == "upper":
                for token in self.token_on_board[player_action[1]]:
                    if token.isupper():
                        to_be_moved = token
                self.token_on_board[player_action[1]].remove(to_be_moved)
                self.token_on_board[player_action[2]].append(to_be_moved)
            
            else:
                for token in self.token_on_board[player_action[1]]:
                    if token.islower():
                        to_be_moved = token
                self.token_on_board[player_action[1]].remove(to_be_moved)
                self.token_on_board[player_action[2]].append(to_be_moved)

        # opponent move update
        if opponent_action[0] == "THROW":
            if self.player == "upper":
                self.token_on_board[opponent_action[2]].append(opponent_action[1])
                self.lower_throw_left-=1
            else:
                self.token_on_board[opponent_action[2]].append(opponent_action[1].upper())
                self.upper_throw_left-=1
        else:
            if self.player == "upper":
                for token in self.token_on_board[opponent_action[1]]:
                    if token.islower():
                        to_be_moved = token
                self.token_on_board[opponent_action[1]].remove(to_be_moved)
                self.token_on_board[opponent_action[2]].append(to_be_moved)
            
            else:
                for token in self.token_on_board[opponent_action[1]]:
                    if token.isupper():
                        to_be_moved = token
                self.token_on_board[opponent_action[1]].remove(to_be_moved)
                self.token_on_board[opponent_action[2]].append(to_be_moved)
        print(self.token_on_board.items())
        self.battle([player_action[2], opponent_action[2]])

    # check for available move for one token/location
    # return a dictionary that maps the location to all possible moves
    def available_moves(self, x):
        result = []
        
        rx, qx = x
        neighbours = self.board[x]
        
        for ry,qy in neighbours:
            # if not self.defeat(self.token_on_board[(ry,qy)][0], self.token_on_board[(rx,qx)][0]):
            result.append(("SLIDE", x, (ry, qy)))
            if (ry,qy) in self.token_on_board:
                
                for letter in self.token_on_board[(ry,qy)]:
                    if self.player == "upper" and letter.isupper():
                        swing_hex = self.board[(ry,qy)]
                        for y in swing_hex:
                            if y not in neighbours and y != x: 
                                result.append(("SWING", x, y))
                    elif self.player == "lower" and letter.islower():
                        swing_hex = self.board[(ry,qy)]
                        for y in swing_hex:
                            if y not in neighbours and y != x: 
                                result.append(("SWING", x, y))

        # print(self.player)
        # print(result)
        return result
    
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
        # remove empty coordinate
        to_be_remove = []
        for coord in self.token_on_board:
            if not self.token_on_board[coord]:
                to_be_remove.append(coord)
        for coord in to_be_remove:
            self.token_on_board.pop(coord)

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
        board[(4,-2)].append((4,-1))
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
