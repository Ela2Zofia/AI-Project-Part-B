from collections import defaultdict
import math
import random
import copy


#limit difference between token's number
BALANCE_LIMIT = 2
LOWER_ORIGIN = -4
UPPER_ORIGIN = 4
LOWER = "lower"
UPPER = "upper"
DEPTH = 3
#key can defeat value
GAME_RULE = {"r":"s","s":"p","p":"r"}


#global variable
#store the board
board = []
#store the player is upper or lower
global_player = ""
#record how many token can be throw
remaining_token = 9
#record throw range
throw_range = 0
#best action in minimax
best_action = ("none", (0, 0), (0, 0))


class Player:

    #key: coordinate, value: tokens in list
    opponent_token_collection = defaultdict(list)
    player_token_collection = defaultdict(list)
    
    def __init__(self, player):
        """
        Called once at the beginning of a game to initialise this player.
        Set up an internal representation of the game state.

        The parameter player is the string "upper" (if the instance will
        play as Upper), or the string "lower" (if the instance will play
        as Lower).
        """
        global LOWER_ORIGIN
        global UPPER_ORIGIN
        global LOWER
        global UPPER
        global global_player
        global board
        global throw_range
        #player
        global_player = player
        #board
        board = generate_board()
        
        #initial throw origin
        if (global_player == LOWER):
            throw_range = LOWER_ORIGIN
        else:
            throw_range = UPPER_ORIGIN
        

    def action(self):
        """
        Called at the beginning of each turn. Based on the current state
        of the game, select an action to play this turn.
        """
        global DEPTH
        global remaining_token
        global best_action

        #check whether should throw
        if (remaining_token > 0):
            action = throw_estimate(self.player_token_collection, self.opponent_token_collection)
            if (action != False):
                return action
        
        #otherwise, move a token
        copy_player_token_collection = copy.deepcopy(self.player_token_collection)
        copy_opponent_token_collection = copy.deepcopy(self.opponent_token_collection)
        minimax(DEPTH, copy_player_token_collection, copy_opponent_token_collection, -math.inf, math.inf, True)

        return best_action


    def update(self, opponent_action, player_action):
        """
        Called at the end of each turn to inform this player of both
        players' chosen actions. Update your internal representation
        of the game state.
        The parameter opponent_action is the opponent's chosen action,
        and player_action is this instance's latest chosen action.
        """
        global best_action

        #update opponent action
        update_token(opponent_action, self.opponent_token_collection, self.player_token_collection)

        #update player's action
        update_token(player_action, self.player_token_collection, self.opponent_token_collection)    

        eliminate_check(self.player_token_collection, self.opponent_token_collection)

        best_action = ("none", (0, 0), (0, 0))


#minimax search with pruning return the best move
#alpha is the best value for max token
#beta is the best value for min token
def minimax(depth, max_collection, min_collection, alpha, beta, isMax):

    global BALANCE_LIMIT
    global LOWER_ORIGIN
    global UPPER_ORIGIN
    global LOWER
    global UPPER
    global DEPTH
    global GAME_RULE
    global global_player
    global board
    global remaining_token
    global throw_range
    global best_action
    
    if (depth == 0):
        return board_evaluation(max_collection, min_collection)

    
    #for max side
    if (isMax):

        #if current collection is empty, the score will be the worest and this action will never be selected
        best_score = math.inf

        #get all min token's type
        min_token_type = ()
        for min_coordinate in min_collection.keys():
            for min_token in min_collection[min_coordinate]:
                min_token_type = min_token_type + (min_token,)

        token_num = 0
        ignore_num = 0

        #search all hex which contain tokens in max token collection
        for max_coordinate in max_collection.keys():

            #the best value and best move
            best_score = -math.inf

            #search all tokens
            for max_token in max_collection[max_coordinate]:

                token_num += 1

                #cut off the token if it can not defeat anyone
                if (GAME_RULE[max_token] not in min_token_type):
                    ignore_num += 1
                    continue

                #search all possible actions of current token
                actions = valid_action(max_coordinate, max_collection)
                for action in actions:

                    #update this possible action into a new token collection
                    new_max_collection = copy.deepcopy(max_collection)
                    new_min_collection = copy.deepcopy(min_collection)
                    update_token(action, new_max_collection,  new_min_collection)
                    eliminate_check(new_max_collection, new_min_collection)
                    

                    #if all opponent has been eliminated, only search one step
                    if (len(list(min_collection.keys())) <= 0):
                        #search for child node
                        max_score= minimax(0, new_max_collection, new_min_collection, alpha, beta, False)
                    
                    #otherwise, search for 3 depth
                    else:
                        max_score= minimax(depth - 1, new_max_collection, new_min_collection, alpha, beta, False)

                    #check score and update action
                    if (max_score > best_score):
                        best_score = max_score
                        #update the best action
                        if (depth == DEPTH):
                            best_action = action


                    #ab pruning
                    alpha = max(alpha, max_score)
                    if beta <= alpha:
                        break
        
        #if all token do not have target, random move
        if ((depth == DEPTH) and ignore_num >= token_num):
            #random pick a move
            for max_coordinate in max_collection.keys():
                for max_token in max_collection[max_coordinate]:
                    best_action = random.choice(valid_action(max_coordinate, max_collection))
                    if not (best_action == [] or best_action == ("none", (0, 0), (0, 0))):
                        return best_score
        
        return best_score

    #for min side
    else:

        #if current collection is empty, the score will be the worest and this action will never be selected
        best_score = -math.inf

        #get all max token's type
        max_token_type = ()
        for max_coordinate in max_collection.keys():
            for max_token in max_collection[max_coordinate]:
                max_token_type = max_token_type + (max_token,)

        #search all hex which contain tokens in min token collection
        for min_coordinate in min_collection.keys():
            
            #the best value and best move
            best_score = math.inf

            #search all tokens
            for min_token in min_collection[min_coordinate]:

                #cut off the token if it can not defeat anyone
                if (GAME_RULE[min_token] not in max_token_type):
                    continue

                #search all possible actions of current token
                actions = valid_action(min_coordinate, min_collection)
                for action in actions:

                    #update this possible action into a new token collection
                    new_min_collection = copy.deepcopy(min_collection)
                    new_max_collection = copy.deepcopy(max_collection)
                    update_token(action, new_min_collection, new_max_collection)
                    eliminate_check(new_min_collection, new_max_collection)
                
                    #search for child node
                    min_score = minimax(depth - 1, new_max_collection, new_min_collection, alpha, beta, True)

                    #check score and update action
                    if (min_score < best_score):
                        best_score = min_score

                    #ab pruning
                    beta = min(alpha, min_score)
                    if beta >= alpha:
                        break

        return best_score
    
                    

#return all possible actions for input token
def valid_action(current_token_coordinate, token_collection):

    global board
    actions = []

    #slide
    slide = "SLIDE"
    #check token's adjacent hex
    for neighbour in board[current_token_coordinate]:
        #avoid to cover friend token
        if neighbour not in token_collection.keys():
            new_action = (slide, current_token_coordinate, neighbour)
            actions.append(new_action)
    
    #swing
    swing = "SWING"
    #check whether there is friend token nearby
    for neighbour in board[current_token_coordinate]:
        if neighbour in token_collection.keys():

            #friend token's neighbour
            for friend_token_neighbour in board[neighbour]:

                #avoid to cover current token's own neighbour or friend token
                if ((friend_token_neighbour not in board[current_token_coordinate]) and (friend_token_neighbour not in token_collection.keys())):
                    new_action = (swing, current_token_coordinate, friend_token_neighbour)
                    actions.append(new_action)

    return actions


#evaluate current situation on the board
def board_evaluation(own_token_collection, opponent_token_collection):

    #the score is evaluated by several factors
    score = 0
    #the manhattan distance to attack opponent
    distance_attack_sum = 0
    #the manhattan distance to avoid opponent
    distance_avoid_sum = 0
    #the manhattan distance with friend
    distance_friend_sum = 0
    #number of both sides' tokens
    opponent_num = 0
    own_side_num = 0
    token_difference = 0

    #two loops are for searching tokens in the same coordinate, the maximum calculation is still 81 times (n^2)
    #search all tokens in own side
    for own_coordinate in own_token_collection.keys():
        for own_token in own_token_collection[own_coordinate]:

            own_side_num += 1

            #check own side's tokens distance with copponent
            for opponent_coordinate in opponent_token_collection.keys():
                for opponent_token in opponent_token_collection[opponent_coordinate]:
                    
                    opponent_num += 1

                    #first factor: negative the Manhattan distance to opponent's tokens which can be defeated
                    #the closer, the better, so is negative
                    if (defeat(own_token, opponent_token) == True):
                        distance_attack_sum -= manhattan_distance(own_coordinate, opponent_coordinate) 

                    #second factor: positive the Manhattan distance to opponent's tokens which can defeat this instance
                    #should be as far as possible, so is positive
                    elif (defeat(own_token, opponent_token) == False):
                        distance_avoid_sum += manhattan_distance(own_coordinate, opponent_coordinate)

            #third feature: negative the distance to friends
            #the closer, the better, so is negative
            #check own side's tokens distance with friend
            for friend_coordinate in own_token_collection.keys():
                for friend_token in own_token_collection[friend_coordinate]:
                    distance_friend_sum -= manhattan_distance(own_coordinate, friend_coordinate)

    opponent_num = opponent_num / own_side_num

    #fourth factor: the difference between two sides' tokens' number
    token_difference = own_side_num - opponent_num

    score = distance_attack_sum * 20 + distance_avoid_sum * 1 + distance_friend_sum * 0.5 + token_difference * 5

    return score


#evaluation whether should throw token 
def throw_estimate(own_token_collection, opponent_token_collection):
    
    action = False

    #Inspection One: throw a token to board if it can defeat opponent's token directly
    action = throw_and_defeat(opponent_token_collection)
    if (action != False):
        return action

    #Inspection Two: throw to keep the balance of tokens
    action = throw_keep_balance(own_token_collection, opponent_token_collection)
    if (action != False):
        return action

    #Inspection Three: no own side's token on the board
    action = throw_to_empty(own_token_collection)
    if (action != False):
        return action

    return False
            

#throw a token to board if it can defeat opponent's token directly
def throw_and_defeat(opponent_token_collection):

    global GAME_RULE

    #search all opponent's tokens
    for opponent_coordinate in opponent_token_collection.keys():
        for opponent_token in opponent_token_collection[opponent_coordinate]:

            #own_token is the token which can defeat the component one
            own_token = GAME_RULE[GAME_RULE[opponent_token]]
            
            #throw if the opponent_token is inside throw's range
            if (coordinate_in_range(opponent_coordinate)):
                throw_coordinate = opponent_coordinate
                action =("THROW", own_token, throw_coordinate)
                update_throw_range()
                return action

    return False


#throw a token to keep the balance of board
def throw_keep_balance(own_token_collection, opponent_token_collection):

    global GAME_RULE
    global board
    global remaining_token
    global throw_range


    #record opponet's tokens' number
    token_sum = {"r" : 0, "p" : 0, "s" : 0}

    #count the opponent token's number
    for opponent_coordinate in opponent_token_collection.keys():
        for token in opponent_token_collection[opponent_coordinate]:
            token_sum[token.lower()] += 1

    #minus opponent token which can be
    for own_coordinate in own_token_collection.keys():
        for token in own_token_collection[own_coordinate]:
            token_sum[GAME_RULE[token.lower()]] -= 1
    
    #throw token if inbalance
    for token in token_sum.keys():
        if (token_sum[token] > 0):

            #own_token is the token which can defeat the component one
            own_token = GAME_RULE[GAME_RULE[token]]

            #throw the new token nearby to a friend token
            for friend_token_coordinate in own_token_collection.keys():
                for friend_token_neighbour_coordinate in board[friend_token_coordinate]:
                    #aviod cover other friend token and in range
                    if friend_token_neighbour_coordinate not in own_token_collection.keys() and coordinate_in_range(friend_token_neighbour_coordinate):

                        throw_coordinate = friend_token_neighbour_coordinate
                        action = ("THROW", own_token, throw_coordinate)
                        update_throw_range()

                        return action
            
            #if there is no friend tokens, throw it on the range line
            throw_coordinate = (throw_range, 0)
            action = ("THROW", own_token, throw_coordinate)
            update_throw_range()
            return action
    
    #otherwise, the board is balance
    return False



#throw if no own side's token
def throw_to_empty(own_token_collection):

    global throw_range

    if not (own_token_collection.keys()):

        #random throw the token
        throw_coordinate = (throw_range, 0)
        own_token = random.choice(["r", "p", "s"])
        action = ("THROW", own_token, throw_coordinate)

        #update range
        update_throw_range()

        return action
    return False


#check throw range
def coordinate_in_range(coordinate):  

    global throw_range
    x = coordinate[0]

    if (global_player == UPPER):
        if x >= throw_range:
            return True
    if (global_player == LOWER):
        if x <= throw_range:
            return True
    return False

#update throw range and number
def update_throw_range():
    global remaining_token
    global throw_range

    if (global_player == UPPER):
        remaining_token -= 1
        throw_range -= 1

    elif (global_player == LOWER):
        remaining_token -= 1
        throw_range += 1



#the manhattan distance
def manhattan_distance(first, second):
    return (abs(first[1] - second[1]) + abs(first[1] - second[1] + first[0] - second[0]) + abs(first[0] - second[0])) / 2



#update the token's new coordinate in tokens' collection
def update_token(action, token_collection, opponent_token_collection):

    global GAME_RULE

    own_token = ""
    new_hex = ()

    if (action[0] == "THROW"):
        #get variables
        new_hex = action[2]
        new_token = action[1]
        own_token = new_token
        #position the token
        token_collection[new_hex].append(new_token)

    #slice or swing token
    elif (action[0] == "SLIDE" or action[0] == "SWING"):
        
        #get variables
        origin_hex = action[1]
        new_hex = action[2]
        own_token = token_collection[origin_hex][0]

        #position token to new coordinate
        token_collection[new_hex].append(own_token)
        
        #remove token from original coordinate
        (token_collection[origin_hex]).remove(own_token)
        #empty the coordinate if no token on it
        if not (token_collection[origin_hex]):
            token_collection.pop(origin_hex)
                


#check whether any token has been eliminated
def eliminate_check(own_side_token_collection, opponent_token_collection):

    global GAME_RULE

    #get the coordinates collection
    own_side_coordinates = copy.deepcopy(list(own_side_token_collection.keys()))
    opponent_coordinates = copy.deepcopy(list(opponent_token_collection.keys()))

    #search all overlapping token cover
    for coordinate in own_side_coordinates:
        if coordinate in opponent_coordinates:
            #records all token's type in current hex
            exist_tokens = []
            for token in own_side_token_collection[coordinate]:
                exist_tokens.append(token)
            for token in opponent_token_collection[coordinate]:
                exist_tokens.append(token)

            #battle in hex
            overlap_token_battle(coordinate, exist_tokens, own_side_token_collection)
            overlap_token_battle(coordinate, exist_tokens, opponent_token_collection)

    #update coordinates collection
    own_side_coordinates = copy.deepcopy(list(own_side_token_collection.keys()))
    opponent_coordinates = copy.deepcopy(list(opponent_token_collection.keys()))

    #check battle inside own side
    for coordinate in own_side_coordinates:
        #while more than one token exist
        if len(list(own_side_token_collection[coordinate])) >= 2:

            #records all token's type in current hex
            exist_tokens = []
            for token in own_side_token_collection[coordinate]:
                exist_tokens.append(token)

            #battle in hex
            overlap_token_battle(coordinate, exist_tokens, own_side_token_collection)
    #check battle inside opponent side
    for coordinate in opponent_token_collection:
        #while more than one token exist
        if len(list(opponent_token_collection[coordinate])) >= 2:

            #records all token's type in current hex
            exist_tokens = []
            for token in opponent_token_collection[coordinate]:
                exist_tokens.append(token)

            #battle in hex
            overlap_token_battle(coordinate, exist_tokens, opponent_token_collection)



#battle on overlapping hex
def overlap_token_battle(coordinate, exist_tokens, token_collection):

    #check single token, remove it if it be defeated
    for token in token_collection[coordinate]:
        #remove the defeated token from collection
        if GAME_RULE[GAME_RULE[token]] in exist_tokens:
            (token_collection[coordinate]).remove(token)
            #empty the coordinate if no token on it
            if not (token_collection[coordinate]):
                token_collection.pop(coordinate)
            





#indentify whether the first token can defeat the second token
def defeat(first, second):
    f = first[0].lower()
    s = second[0].lower()
    return GAME_RULE[f.lower()] == s.lower()



#generate board
def generate_board():

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