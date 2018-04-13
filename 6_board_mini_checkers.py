'''
Mini checkers application is built using a 6x6 board.
Mini checkers does not consider the piece as a king.
The win state is determined by  number of pieces that remains towards the end state of the game.
'''

# ----------------------import  libraries--------------------- #
import os, sys
import logging as logger  # adding logs

import pygame as pg  # pygame library for gui
import datetime
from random import randint

from copy import deepcopy

#  ---------- Global Variables ---------------#

# --loggers
log_level = 'DEBUG'
logfile = 'logs/logfile'

# -- Piece objects
black, white = (), ()

# -- GUI
window_size = (386, 450)  # size of board in pixels
title = 'Mini Checkers'  # Title of the game
board_size = 6  # board is 6x6 squares
background_image = 'board_brown_6x6.png'  # name of the 6x6 png file
font_file = 'fonts/freesansbold.ttf'  # To display characters in font styles
left = 1  # click left mouse button once
image_size = (386, 384)
fps = 5  # framerate of the scene (to save cpu time)
btn_font = ()   # Font for button text

blk_txt = (0, 0, 0)
yellow = (255, 255, 51)
green = (51, 255, 51)
red = (51, 255, 51)

# -- initialize game configuration
ai_playes = 1  # ai plays first
turn = 'nil'

# -- moves
selected = (0, 1)  # tracks the piece selected by human
best_move = ()  # keep track of the best move possible

# -- alpha-beta counter variables
init_start_time = 0  # track start time of the game
node = 0  # track max nodes generated
max_prun_cntr = 0  # max prune counter
min_prun_cntr = 0  # min prune counter
max_depth = 0  # max_depth traversed
ai_max_think_time = 3  # max think time for ai to decide the move
time_elapsed = 0

# -- Utility variables
start = True


# ------------- Classes ------------#

# Class for Player type - Human or AI
class Player:
    def __init__(self, type, color, ply_depth):
        self.type = type
        self.color = color
        self.ply_depth = ply_depth


# Class to create black and white piece
class Piece:
    def __init__(self, color):
        self.color = color


#   ---------- Utilities ---------------#


# display messages for user on screen
def display_message(message):
    text = font.render(' ' + message + ' ', True, (255, 255, 255), (120, 195, 46))  # create message
    textRect = text.get_rect()  # Creates rectangle
    textRect.centerx = screen.get_rect().centerx
    textRect.centery = screen.get_rect().centery - 30
    screen.blit(text, textRect)


# will display the winner
def display_winner(winner):
    global board  # we are resetting the global board

    if winner == 'draw':
        display_message("draw, 'select button for new  game'")
    else:
        display_message(winner + " wins, 'select button for new  game'")

    pg.display.flip()  # display scene from buffer


# draw pieces on the board
def draw_piece(row, column, color):
    # find the center pixel for the piece
    posX = ((image_size[0] / 6) * column) - (image_size[0] / 6) / 2
    posY = ((image_size[1] / 6) * row) - (image_size[1] / 6) / 2
    posX = int(posX)
    posY = int(posY)

    # set color for piece
    if color == 'black':
        border_color = (255, 255, 255)
        inner_color = (0, 0, 0)
    elif color == 'white':
        border_color = (0, 0, 0)
        inner_color = (255, 255, 255)

    pg.draw.circle(screen, border_color, (posX, posY), 15)  # draw piece border
    pg.draw.circle(screen, inner_color, (posX, posY), 13)  # draw piece

# drawing buttons for game level
def draw_button(glevel,w_pos ):

    global btn_font
    textSurface = btn_font.render(glevel, True, blk_txt)
    textRect = textSurface.get_rect()
    textRect.center = (w_pos, 415)
    screen.blit(textSurface, textRect)



#   ---------- Initialize -----------------#


def init_player(type, color, ply_depth):
    return Player(type, color, ply_depth)  # Create Player object


def init_piece(color):
    return Piece(color)  # creating black and white pieces for board


def init_board():  # Initialize the 6x6 checker board

    board_arr = [
        [0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 0],
        [0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0],
        [0, -1, 0, -1, 0, -1],
        [-1, 0, -1, 0, -1, 0]
    ]

    for m in range(6):
        for n in range(6):
            if board_arr[m][n] == 1:
                board_arr[m][n] = init_piece('black')
            elif board_arr[m][n] == -1:
                board_arr[m][n] = init_piece('white')

    return board_arr


def init_game(level):  # Initialize game settings
    global black, white
    global turn, ai_playes

    if level == 1:  # Level 1, 2, 3  easy, medium, difficult respectively
        white = init_player('human', 'white', randint(1, 4))  # Initialize human player
        black = init_player('ai', 'black', randint(1, 4))  # Initialize AI player
        board = init_board()  # Create board
        turn = 'nil'  # reset the initial values for human or ai first
        ai_playes = 1
    elif level == 2:
        white = init_player('human', 'white', randint(5, 8))  # Initialize human player
        black = init_player('ai', 'black', randint(5, 8))  # Initialize AI player
        board = init_board()  # Create board
        turn = 'nil'  # reset the initial values for human or ai first
        ai_playes = 1
    else:
        white = init_player('human', 'white', randint(9, 15))  # Initialize human player
        black = init_player('ai', 'black', randint(9, 15))  # Initialize AI player
        board = init_board()  # Create board
        turn = 'nil'  # reset the initial values for human or ai first
        ai_playes = 1

    return board


# ------------ Checker Moves -----------#

def mouse_click(pos):
    global selected

    # only go ahead if we can actually play :)
    if (turn != 'black' and white.type != 'ai') or (turn != 'white' and black.type != 'ai'):
        column = pos[0] / (image_size[0] / board_size)
        row = pos[1] / (image_size[1] / board_size)
        column = int(column)
        row = int(row)  # row, column location of the piece clicked

        if row < 0 or row > 5:
            return  # return if the mouse click is outside the image window

        if column < 0 or column > 5:
            return

        if board[row][column] != 0 and board[row][column].color == turn:
            selected = row, column  # select a piece to play
        else:
            moves = possible_moves(board, turn)
            for i in range(len(moves)):
                if selected[0] == moves[i][0] and selected[1] == moves[i][1]:
                    if row == moves[i][2] and column == moves[i][3]:
                        make_move(selected, (row, column), board)  # make the move
                        switch_turn()  # end turn


# Count the list of capture moves for AI
def count_capture_moves(board, player):
    moves = []

    # ...check for a possible capture move
    for m in range(6):
        for n in range(6):
            if board[m][n] != 0 and board[m][n].color == player:  # for all the pieces on the board...
                if is_capture_move([m, n], [m + 1, n + 1], [m + 2, n + 2], board):
                    moves.append([m, n, m + 2, n + 2])

                if is_capture_move([m, n], [m - 1, n + 1], [m - 2, n + 2], board):
                    moves.append([m, n, m - 2, n + 2])

                if is_capture_move([m, n], [m + 1, n - 1], [m + 2, n - 2], board):
                    moves.append([m, n, m + 2, n - 2])

                if is_capture_move([m, n], [m - 1, n - 1], [m - 2, n - 2], board):
                    moves.append([m, n, m - 2, n - 2])
    return moves


def possible_moves(board, player):
    moves = []  # will store available jumps and moves

    # ...check for a possible capture move
    for m in range(6):
        for n in range(6):
            if board[m][n] != 0 and board[m][n].color == player:  # for all the pieces on the board...
                if is_capture_move([m, n], [m + 1, n + 1], [m + 2, n + 2], board):
                    moves.append([m, n, m + 2, n + 2])

                if is_capture_move([m, n], [m - 1, n + 1], [m - 2, n + 2], board):
                    moves.append([m, n, m - 2, n + 2])

                if is_capture_move([m, n], [m + 1, n - 1], [m + 2, n - 2], board):
                    moves.append([m, n, m + 2, n - 2])

                if is_capture_move([m, n], [m - 1, n - 1], [m - 2, n - 2], board):
                    moves.append([m, n, m - 2, n - 2])

    if len(moves) == 0:  # piece doesn't make any jump
        # ...check for all regular moves
        for m in range(6):
            for n in range(6):
                if board[m][n] != 0 and board[m][n].color == player:  # for all pieces on the board...
                    if is_regular_move([m, n], [m + 1, n + 1], board):
                        moves.append([m, n, m + 1, n + 1])

                    if is_regular_move([m, n], [m - 1, n + 1], board):
                        moves.append([m, n, m - 1, n + 1])

                    if is_regular_move([m, n], [m + 1, n - 1], board):
                        moves.append([m, n, m + 1, n - 1])

                    if is_regular_move([m, n], [m - 1, n - 1], board):
                        moves.append([m, n, m - 1, n - 1])

    return moves  # return the list with available jumps or moves


def is_capture_move(src, via, dest, board):
    # check outside the board
    if dest[0] < 0 or dest[0] > 5 or dest[1] < 0 or dest[1] > 5:
        return False

    # does destination has a piece already
    if board[dest[0]][dest[1]] != 0:
        return False

    # check jump
    if board[via[0]][via[1]] == 0:
        return False

    # for white piece
    if board[src[0]][src[1]].color == 'white':
        if dest[0] > src[0]: return False
        if board[via[0]][via[1]].color != 'black': return False  # only jump blacks
        return True  # jump is possible

    # for black piece
    if board[src[0]][src[1]].color == 'black':
        if dest[0] < src[0]: return False
        if board[via[0]][via[1]].color != 'white': return False  # only jump whites
        return True  # jump is possible


# will return true if the move is legal
def is_regular_move(src, dest, board):
    # check outside the board
    if dest[0] < 0 or dest[0] > 5 or dest[1] < 0 or dest[1] > 5:
        return False

    # check does destination has a piece already
    if board[dest[0]][dest[1]] != 0: return False

    # for white piece
    if board[src[0]][src[1]].color == 'white':
        if dest[0] > src[0]: return False  # only move up
        return True  # move is possible

    # for black piece
    if board[src[0]][src[1]].color == 'black':
        if dest[0] < src[0]: return False  # only move down
        return True  # move is possible


# make the final move on a board
def make_move(a, b, board):
    board[b[0]][b[1]] = board[a[0]][a[1]]  # make the move
    board[a[0]][a[1]] = 0  # delete the source
    if (a[0] - b[0]) % 2 == 0:  # we made a jump...
        board[int((a[0] + b[0]) / 2)][int((a[1] + b[1]) / 2)] = 0  # delete the jumped piece


# end or switch turn
def switch_turn():
    global turn  # use global variables

    if turn != 'black':
        turn = 'black'
    else:
        turn = 'white'


# ------------ AI ----------------------#

# ai makes the turn..
def ai_play(player):
    logger.debug('....Inside AI plays method.....')

    global board, init_start_time

    moves = count_capture_moves(board, player.color)

    if len(moves) == 1:
        logger.info('...AI skips alpa-beta and takes capture move at %s,%s: ', moves[0][0], moves[0][1])
        make_move((moves[0][0], moves[0][1]), (moves[0][2], moves[0][3]), board)  # make move on board copy
        switch_turn()
        return

    init_start_time = datetime.datetime.now()

    # ai uses alpha beta to select its best move
    logger.debug('....AI initiates alpha beta algorithm - First Call!....')
    alpha = mini_max(player.color, board, 0, -1000, +1000)

    logger.info("....Printing game statistics...")
    logger.info('Total Nodes generated: %s ', node)
    logger.info('Total prunes by Max: %s', max_prun_cntr)
    logger.info('Total prunes by Min: %s', min_prun_cntr)
    logger.info('Max Depth Traversed: %s ', max_depth)

    if alpha == -1000:  # no more moves available...
        if player.color == white:
            display_winner("black")
        else:
            display_winner("white")

    logger.debug('Best move selected by CPU from :%s, to %s', best_move[0], best_move[1])
    make_move(best_move[0], best_move[1], board)  # make the move on board

    switch_turn()  # end turn


# mini max with alpha beta pruning implementation
def mini_max(player, board, ply, alpha, beta):
    logger.debug('... Calling Minimax for ply depth at %s: ', ply)

    global node, max_prun_cntr, min_prun_cntr, best_move, max_depth, time_elapsed  # Declaring global variables

    # Find the current execution time
    time_elapsed = (datetime.datetime.now() - init_start_time).seconds

    # Compare ply_depth values initialized at the start of the game
    if player != 'black':
        ply_depth = white.ply_depth
    else:
        ply_depth = black.ply_depth

    # Check if the game has terminated
    end = end_game(board)

    if ply > max_depth:
        max_depth = ply

    if end[0] == 0 or end[1] == 0:
        logger.debug('.. Search tree terminating for conditions on  end state black %s, white %s', end[0], end[1])
        score = eval_heuristic(board, player)
        logger.debug('Terminating game with score %s', score)
        return score

    moves = possible_moves(board, player)

    if player == turn:  # Max play's : Computer's move
        logger.debug('Calling Max  at ply_depth %s: ', ply)

        if time_elapsed >= ai_max_think_time:  # check if time exceeds max permissible search time
            logger.info(' Search time passed beyond max time %s at Max, backtracking at depth %s... ', time_elapsed,
                        ply)
            return eval_heuristic(board, player)

        if ply >= ply_depth:  # Implementing iterative deepening
            logger.debug('Reached depth limit of %s, for Max backtracking starts....', ply)
            score = eval_heuristic(board, player)
            return score


        for i in range(len(moves)):
            logger.debug('AI plays total moves %s in %s', len(moves), player)

            board_copy = deepcopy(board)  # Creates a new node
            node += 1  # Node counter to keep count of every node generated

            make_move((moves[i][0], moves[i][1]), (moves[i][2], moves[i][3]), board_copy)  # make move on board copy

            if player == 'white':
                player = 'black'
            else:
                player = 'white'  # switch turns for black and white to play max and min

            score = mini_max(player, board_copy, ply + 1, alpha, beta)

            if score > alpha:
                if ply == 0:
                    best_move = (moves[i][0], moves[i][1]), (moves[i][2], moves[i][3])
                logger.debug('Max selects best move at %s,%s for source %s, %s', moves[i][2], moves[i][3], moves[i][0],
                             moves[i][1])
                alpha = score

            if alpha >= beta:
                max_prun_cntr += 1  # count the number of times max prunes
                return alpha

        return alpha

    else:  # Min Function Human plays Min
        logger.debug('Calling Min  at ply_depth %s: ', ply
                     )
        if time_elapsed >= ai_max_think_time:  # check if time exceeds max permissible search time
            logger.info(' Search time passed beyond max time %s at Min, backtracking at depth %s... ', time_elapsed,
                        ply)
            return eval_heuristic(board, player)

        if ply >= ply_depth:  # Implementing iterative deepening
            logger.debug('Reached depth limit of %s for Min, backtracking starts....', ply)
            score = eval_heuristic(board, player)
            return score

        for i in range(len(moves)):
            logger.debug('AI plays total moves %s in %s', len(moves), player)

            board_copy = deepcopy(board)  # Creates a new node
            node += 1  # Node counter to keep count of every node generated

            make_move((moves[i][0], moves[i][1]), (moves[i][2], moves[i][3]), board_copy)  # make move on board copy

            if player == 'white':
                player = 'black'
            else:
                player = 'white'  # switch turns for black and white to play max and min

            score = mini_max(player, board_copy, ply + 1, alpha, beta)

            if score < beta:
                beta = score

            if alpha >= beta:
                min_prun_cntr += 1  # count the number of times max prunes
                return beta

        return beta


# Heuristic function calculates the terminal state scores
def eval_heuristic(board, player):
    black, white = 0, 0

    for m in range(6):
        for n in range(6):
            if board[m][n] != 0 and board[m][n].color == 'black':
                black += 100  # count all the black piece
            elif board[m][n] != 0 and board[m][n].color == 'white':
                white += 100  # count all the white pieces

    if player == 'white':
        return white - black
    else:
        return black - white


# ------------ tracking game scores------------#

# count number of piece on the board

def end_game(board):
    black, white = 0, 0  # keep track of score
    for m in range(6):
        for n in range(6):
            if board[m][n] != 0:
                if board[m][n].color == 'black':
                    black += 1  # count black piece
                else:
                    white += 1  # count white piece

    return black, white


# check for terminating state of the game
def is_game_terminated(board):
    moves_white = possible_moves(board, 'white')
    moves_black = possible_moves(board, 'black')
    if len(moves_white) == 0 or len(moves_black) == 0:
        return True
    else:
        return False


# ------------ GAME starts here --------------#

logger.basicConfig(level=logger.INFO, filename=logfile, filemode="a+",
                   format="%(asctime)-15s %(levelname)-8s %(message)s")  # To add

logger.info("---------------- Loading Checkers GUI ------------------------------------")

pg.init()  # Initialize pygame

board = init_game(1)  # Game is defaulted to play at level 1

# creating the gui elements

try:
    bg = [255, 255, 255]
    screen = pg.display.set_mode(window_size)  # set window size
    pg.display.set_caption(title)  # set title of the window
    clock = pg.time.Clock()  # create clock to control refresh rate

    file_path = os.path.join('images', background_image)  # Load Images onto the window

    background = pg.image.load(file_path)  # load background
    font = pg.font.Font(font_file, 11)  # font for the messages
    btn_font = pg.font.Font(font_file, 15)  # font for the messages
    screen.fill(bg)  # Creating solid white background

    btn_easy = pg.Rect(130, 400, 25, 25)  # Initialize buttons
    btn_moderate = pg.Rect(170, 400, 25, 25)
    btn_hard = pg.Rect(210, 400, 25, 25)

    pg.draw.rect(screen, [255, 255, 51], btn_easy)  # draw yellow button
    draw_button('L1', 143)  # Drawing Levels on buttons

    pg.draw.rect(screen, [51, 255, 51], btn_moderate)  # draw green button
    draw_button('L2', 183)

    pg.draw.rect(screen, [255, 51, 51], btn_hard)  # draw red button
    draw_button('L3', 223)


    logger.debug('Pygame successfully initialized! ')

except pg.error as message:
    logger.error('Error loading pygame %s', message)  # Catch pygame exception
except Exception as e:
    print(e)
    logger.error('Error in gui set up %s', e)  # Catch  all other exceptions

#  Monitor Mouse click events
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == left:
            mouse_pos = event.pos
            ai_playes = 2
            if btn_easy.collidepoint(mouse_pos):
                logger.info('Level 1 selected!......')
                board = init_game(1)  # mouse click
                continue
            elif btn_moderate.collidepoint(mouse_pos):
                logger.info('Level 2 selected!......')
                board = init_game(2)  # mouse click
                continue
            elif btn_hard.collidepoint(mouse_pos):
                logger.info('Level 3 selected!......')
                board = init_game(3)  # mouse click
                continue
            else:
                turn = 'white'
                mouse_click(event.pos)  # mouse click
        elif event.type == pg.KEYDOWN and event.key == pg.K_c:
            if ai_playes == 1:
                logger.info(' AI moves first!.....')
                turn = 'black'
                ai_playes = 2
                display_message('AI THINKING...')
                ai_play(black)

        screen.blit(background, (0, 0))  # Blits the sreen

        if turn == 'nil':
            display_message('Click to start the game')  # Prompt the user or ai to start
        elif turn != 'white':
            display_message('AI Thinking.....')  # AI plays
        elif (turn != 'black' and white.type == 'human') or (turn != 'white' and black.type == 'human'):
            display_message('YOUR TURN')  # Prompt user to play

        # paint pieces on the board
        for m in range(6):
            for n in range(6):
                if board[m][n] != 0:
                    draw_piece(m + 1, n + 1, board[m][n].color)

        # show introduction message when the game is loaded first
        if start:
            display_message('Welcome to ' + title)
            start = False

        # check state of game
        end = end_game(board)
        if end[1] == 0:
            display_winner("Black")  # Black pawns are more and black wins
        elif end[0] == 0:
            display_winner("White")  # White pawns are more and white wins

        elif is_game_terminated(board):
            count = end_game(board)
            w = count[1]
            b = count[0]
            if b == w:
                display_winner("draw")
            elif b > w:
                display_winner("Black")
            else:
                display_winner("White")
        else:
            pg.display.flip()  # display scene from buffer

        if turn == 'nil':
            continue  # do nothing if nobody has initiated the game

        # ai play's
        if turn != 'black' and white.type == 'ai':
            ai_play(white)  # white ai turn
        elif turn != 'white' and black.type == 'ai':
            ai_play(black)  # black ai turn

        clock.tick(fps)  # saves cpu time
