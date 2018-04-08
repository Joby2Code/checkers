'''
Mini checkers application is built using a 6x6 board.
Mini checkers does not consider the piece as a king.
The win state is determined by what number of pieces that remains towards the end state of the game.
'''

# ----------------------import  libraries--------------------- #
import os, sys
import logging  # adding logs

import pygame as pg  # pygame library for gui
import datetime

from copy import deepcopy

#  ---------- Global Variables ---------------#

# --loggers
log_level = 'logging.DEBUG'
logfile = 'logs/logfile'

# -- Piece objects
black, white = (), ()

# -- GUI
window_size = (386, 450)  # size of board in pixels
title = 'Mini Checkers'
background_image = 'board_brown_6x6.png'  # name of the 6x6 png file
font_file = 'fonts/freesansbold.ttf'  # To display characters in font styles
left = 1  # click left mouse button once

# -- moves
ai_playes = 1  # ai plays first
turn = 'white'


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
            if board_arr[m, n] == 1:
                board_arr[m, n] = init_piece('black')
            elif board_arr[m, n] == -1:
                board_arr[m, n] = init_piece('white')

    return board_arr


def init_game(level):  # Initialize game settings
    global black, white

    if level == 1:  # Level 1, 2, 3  easy, medium, difficult respectively
        white = init_player('human', 'white', 2)  # Initialize human player
        black = init_player('ai', 'black', 2)  # Initialize AI player
        board = init_board()  # Create board
    elif level == 2:
        white = init_player('human', 'white', 8)  # Initialize human player
        black = init_player('ai', 'black', 8)  # Initialize AI player
        board = init_board()  # Create board
    else:
        white = init_player('human', 'white', 12)  # Initialize human player
        black = init_player('ai', 'black', 12)  # Initialize AI player
        board = init_board()  # Create board

    return board


# ------------ Checker Moves -----------#


# ------------ AI ----------------------#


# ------------ GAME starts here --------------#

logger = logging.basicConfig(level=logging.INFO, filename=logfile, filemode="a+",
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

    screen.fill(bg)  # Creating solid white background

    btn_easy = pg.Rect(130, 400, 25, 25)  # Initialize buttons
    btn_moderate = pg.Rect(170, 400, 25, 25)
    btn_hard = pg.Rect(210, 400, 25, 25)

    pg.draw.rect(screen, [255, 255, 51], btn_easy)  # draw yellow button
    pg.draw.rect(screen, [51, 255, 51], btn_moderate)  # draw green button
    pg.draw.rect(screen, [255, 51, 51], btn_hard)  # draw red button

    logger.debug('Pygame successfully initialized! ')

except pg.error as message:
    logger.debug('Error loading pygame', message)  # Catch pygame exception
except Exception as e:
    logger.debug('Error in gui set up', e)  # Catch  all other exceptions

#  Monitor Mouse click events
while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            sys.exit()
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == left:
            mouse_pos = event.pos
            ai_playes = 2
            if btn_easy.collidepoint(mouse_pos):
                logger.debug('Level 1 selected!......')
                board = init_game(1)  # mouse click
                ai_playes = 1
            elif btn_moderate.collidepoint(mouse_pos):
                logger.debug('Level 2 selected!......')
                board = init_game(2)  # mouse click
                ai_playes = 1
            elif btn_hard.collidepoint(mouse_pos):
                logger.debug('Level 3 selected!......')
                board = init_game(3)  # mouse click
                ai_playes = 1
            else:
        # mouse_click(event.pos)  # mouse click
        elif event.type == pg.K_c:
            if ai_playes == 1:
                logger.debug(' AI makes the first move.....')
                turn = 'black'
                ai_playes = 2

        screen.blit(background, (0, 0))  # Blits the sreen

        if (turn != 'black' and white.type == 'human') | | (turn != 'white' and black.type == 'human'):
            display_message('YOUR TURN')
        else:
            display_message(' AI Thinking')

        # if event.key == pygame.K_F1:  # when pressing 'F1'...
        # cpu_play(black)
        # cpu_plays -= 1
        # cpu_again = False
