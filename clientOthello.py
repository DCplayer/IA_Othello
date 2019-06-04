import copy
from random import randint
import math
import socketio
import random
import math

tileRep = ['_', 'X', 'O']
N = 8

def isOnBoard(x, y):
    if -1 < x < 8 and -1 < y < 8:
        return True
    return False


def heuristic(board, tile):
    numero = 0
    #esquinas
    great_choices=[0, 7, 56, 63]

    #orillas
    good_choices=[2, 3, 4, 5, 16, 23, 24, 31, 32, 39, 40, 47, 58, 59, 60, 61]

    #inner_ring
    bad_choices =[10, 11, 12, 13, 17, 22, 25, 30, 33, 38, 41, 46, 50, 51, 52, 53]

    #precorners
    worst_choices=[1, 6, 8, 9, 14, 15, 41, 49, 54, 55, 57, 62]

    for i in great_choices:
        if board[i] == tile:
            numero += 4

    for i in good_choices:
        if board[i] == tile:
            numero += 2

    for i in bad_choices:
        if board[i] == tile:
            numero -= 2

    for i in worst_choices:
        if board[i] == tile:
            numero -= 4

    return numero


def value(board, tile):
    otherTile = 1
    if tile == 1:
        otherTile = 2

    return board.count(otherTile) - board.count(tile)


def alphabeta(board, depth, a, b, maximazingPlayer, tile):
    newBoard, moves = legal_move(board, tile)
    if depth == 0 or board.count(1) + board.count(2) == N**2 or not newBoard:
        return  value(board, tile) + heuristic(board, tile)

    otherTile = 1
    if tile == 1:
        otherTile = 2

    bestcoordinate = 0
    if maximazingPlayer:
        for i in newBoard:
            # print(i)
            bestvalue = alphabeta(i, depth-1, a, b, False, tile)
            # print(bestvalue)
            if bestvalue > a:
                a = bestvalue
                bestcoordinate = i
            if a>=b:
                break

        if bestcoordinate == 0:
            return 0
        else:
            return moves[newBoard.index(bestcoordinate)]
    else:
        for i in newBoard:
            bestvalue = alphabeta(i, depth-1, a, b, True, otherTile)
            if bestvalue < b:
                b = bestvalue
                bestcoordinate = i

            if a>=b:
                break
        if bestcoordinate == 0:
            return 0
        else:
            return moves[newBoard.index(bestcoordinate)]


def legal_move(board, tile):
    newboard = []
    move = []
    for i in range(N**2):
        resolve = isValidMove(board, tile, math.floor(i/N), i % N)
        if not resolve:
            continue
        newboard.append(resolve)
        move.append(i)
    return newboard, move



def isValidMove(board, tile, x, y):
    index = x * N + y

    if board[index] != 0 or not isOnBoard(x, y):
        return False

    testboard = copy.deepcopy(board)
    testboard[index] = tile

    otherTile = 1
    if tile == 1:
        otherTile = 2

    tilesToFlip = []
    for xd, yd in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        i, j = x, y

        i += xd
        j += yd

        if isOnBoard(i, j) and testboard[i*N+j] == otherTile:
            i += xd
            j += yd
            if not isOnBoard(i, j):
                continue
            while testboard[i*N + j] == otherTile:
                i += xd
                j += yd

                if not isOnBoard(i, j):
                    break
            if not isOnBoard(i, j):
                continue
            if testboard[i*N + j] == tile:
                while True:
                    i -= xd
                    j -= yd

                    if i == x and j == y:
                        break
                    tilesToFlip.append([i, j])

    if len(tilesToFlip) > 0:
        for i in tilesToFlip:
            index = i[0] * N + i[1]
            testboard[index] = tile
        return testboard

    else:
        return False


def ix(row, col):
    return (row-1)*N + 'abcdefgh'.index(col)


def humanBoard(board):
    result = 'A B C D E F G H'
    for i in range(len(board)):
        if i % N == 0:
            result += '\n \n' + str((int(math.floor(i / N)) + 1)) + ' '

        result += ' ' + tileRep[board[i]] + ' '

    return result

def validateHumanPosition(position):
    validated = len(position) == 2
    
    if validated:
        row = int(position[0])
        col = position[1].lower()
        return (1 <= row and row <= N) and ('abcdefgh'.index(col) >= 0)
    
    else:
        return False

#socket =  socketio.Client()
socket = socketio.Client()
socket.connect('http://192.168.1.148:4000')
userName = 'Diego Castaneda'
tournamentID = 142857

##cliente conectado 
print("Conecta: " + userName)

@socket.on('connect')
def on_connect():
    print("Conecta: " + userName)
    socket.emit('signin',{
            'user_name': userName,
            'tournament_id': tournamentID,
            'user_role': 'player'

        })

@socket.on('ready')
def on_ready(data):
    print('About to move. Board: \n')
    #print(humanBoard(data[board]))
    print('\n Requisting move....')

    print(humanBoard(data['board']))
    socket.emit('play',{
        'player_turn_id': data['player_turn_id'], 
        'tournament_id': tournamentID,
        'game_id': data['game_id'],
        'movement': alphabeta(data['board'], 5, -10000, 10000, True, data['player_turn_id'])
        })

@socket.on('finish')
def on_finish(data):
    print('Game '+ str(data['game_id'])+' has finished')
    print('Ready to play again!')
    
        
    socket.emit('player_ready',{
        'tournament_id': tournamentID,
        'game_id': data['game_id'],
        'player_turn_id': data['player_turn_id']
        })
