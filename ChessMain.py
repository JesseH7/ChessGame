#--------------------------------------------------------------------------------------------------------
#Main file, which will be responsible to handling user input and displaying the current GameState object.
#--------------------------------------------------------------------------------------------------------
# (404,136) is top left of the board
import pygame as p
import ChessEngine
import time
import pyodbc
from operator import itemgetter, attrgetter, methodcaller
import tkinter as tk
from tkinter import ttk
from tkinter import *

WIDTH = HEIGHT = 560
DIMENSION = 8 #Chess board dimensions are 8x8
SQ_SIZE = HEIGHT // DIMENSION
#MAX_FPS = 15
IMAGES = {}
#---------------------------------------------------------------------------
#Initialise a global dictionary of images. This will be called once in main.
#---------------------------------------------------------------------------

def loadImages():
    pieces = ["wP","wR","wN","wB","wK","wQ","bP","bR","bN","bB","bK","bQ"]
    for piece in pieces:
        IMAGES[piece] = p.image.load("70x70_images/"+piece+".png")

#-------------------------------------------------------------------------------
#The main driver for the code. This will handle user input and updating graphics
#-------------------------------------------------------------------------------

def main(t, userText1, userText2):
    p.init()
    screen = p.display.set_mode((1368,862))
    p.display.set_caption("Chess Game")
    clock = p.time.Clock()
    screen.fill(p.Color("gray25"))
    loadImages()
    gs = ChessEngine.GameState()
    validMoves = gs.getValidMoves()
    moveMade = False #Flag variable for when a move is made
    capturedPieces = [] #List for all captured pieces
    running = True
    sqSelected = () #No square is selected initially. Keep track of the last click of the user (tuple:(row,col))
    playerClicks = [] #Keep track of the player clicks (two tuples: [(6,4), (4,4)] )

    #Initialises the clock and some variables used for the timers
    clock = p.time.Clock()
    counterW = t
    counterB = t
    p.time.set_timer(p.USEREVENT, 1000)
    timeformatW = ""
    timeformatB = ""

    global timerRunOut
    timerRunOut = False
    global runOnce
    runOnce = 1
    print(runOnce)
    #Main loop
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False     
            if e.type == p.KEYDOWN:
                if e.key == p.K_l:
                    leaderboard()
            if gs.winner == "n/a":
                drawBlackScore(screen, gs)
                drawWhiteScore(screen, gs) 
                #Mouse handler
                if e.type == p.MOUSEBUTTONDOWN:
                    location = p.mouse.get_pos() #(x,y) location of mouse
                    print(location)
                    col = location[0]//SQ_SIZE -6
                    row = location[1]//SQ_SIZE -2
                    print("Column:",col,", Row:",row)
                    if sqSelected == (row,col) or (row>7 or row<0 or col>7 or col<0): #The user clicked the same square twice or clicked off the board
                        sqSelected = () #deselect
                        playerClicks = [] #clear player's clicks
                    else: 
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) #append for both 1st and 2nd clicks
                    if len(playerClicks) == 2: #After the 2nd click
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print("Start Row:",playerClicks[0][0], "Start Col:",playerClicks[0][1])
                        print("Chess Notation:",move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                if gs.board[playerClicks[1][0]][playerClicks[1][1]] != "--": #Is the captured piece not an empty square?
                                    capturedPieces.append(gs.board[playerClicks[1][0]][playerClicks[1][1]])                                                             
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                sqSelected = () #Reset user clicks
                                playerClicks = []
                                gs.check = False                           
                        if not moveMade:
                            playerClicks = [sqSelected]
                        
                #Key handler
                elif e.type == p.KEYDOWN:
                    if e.key == p.K_z: #Undo move when 'z' key is pressed
                        if gs.checkMate == False:
                            gs.undoMove()
                            clearResultText(screen, gs)
                            moveMade = True
                
                if counterB <= 1800 and counterW <= 1800:
                    if e.type == p.USEREVENT and counterW >0 and gs.whiteToMove == True:
                        counterW -= 1

                    if e.type == p.USEREVENT and counterB >0 and gs.whiteToMove == False:               
                        counterB -= 1

                    if gs.checkMate == True or gs.staleMate == True:
                        counterB = 0
                        counterW = 0

                    if counterB == 0:
                        gs.winner = "White"
                        timerRunOut = True
                    if counterW == 0:
                        gs.winner = "Black"
                        timerRunOut = True

                if moveMade:
                    validMoves = gs.getValidMoves()
                    moveMade = False

                drawGameState(screen, gs, validMoves, sqSelected, capturedPieces, counterB, counterW, userText1, userText2)
           
                #clock.tick(MAX_FPS)
                p.display.flip()
                clock.tick(60)
            else:
                drawResultText(screen, gs, timerRunOut, userText1, userText2)
                p.display.flip()

            

                    
            



            

#------------------------------------------------------------
#Resonsible for all the graphics within a current game state.
#------------------------------------------------------------

def drawGameState(screen, gs, validMoves, sqSelected, capturedPieces, counterB, counterW, userText1, userText2):
    drawBoard(screen) #draw squares on the board
    drawPieces(screen, gs.board) #draw pieces on top of the squares
    drawPotentialMoves(screen, gs, validMoves, sqSelected)
    drawPlayer1(screen, userText1)
    drawPlayer2(screen, userText2) 
    drawCoordinates(screen)
    drawPieceValues(screen, gs)
    drawScoreDifference(screen, capturedPieces) 
    blackTime(screen, counterB)
    whiteTime(screen, counterW)
    drawCheckText(screen, gs)


#-----------------------------
#Draw the squares on the board
#-----------------------------

def drawBoard(screen):
    colors = [p.Color("white"),p.Color("royalblue3")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE+404,r*SQ_SIZE+137,SQ_SIZE,SQ_SIZE))



#--------------------------------------------------------------
#Draw the pieces on the board using the current GameState.board
#--------------------------------------------------------------

def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c*SQ_SIZE+404, r*SQ_SIZE+137, SQ_SIZE, SQ_SIZE))

#--------------------------------------------------------------
#Draws the rank and file coordinates to the sides of the board
#--------------------------------------------------------------
def drawCoordinates(screen):
    font = p.font.Font('freesansbold.ttf', 20)
    #Generates the rank numbers at the side of the board
    ranknum = ["1","2","3","4","5","6","7","8"]
    x_startpos = 395
    y_startpos = 662
    for x in range(0,8):
        text = font.render(ranknum[x], True,"white","gray25")
        textRect = text.get_rect()
        textRect.center = (x_startpos,y_startpos)
        y_startpos = y_startpos - 70
        screen.blit(text, textRect)
    #Generates the file letters at the bottom of the board
    x_startpos = 438
    y_startpos = 710
    fileletter = ["A","B","C","D","E","F","G","H"]
    for i in range(0,8):
        text = font.render(fileletter[i], True,"white","gray25")
        textRect = text.get_rect()
        textRect.center = (x_startpos,y_startpos)
        x_startpos = x_startpos + 70
        screen.blit(text, textRect)

#Draws the potential moves for a piece that is clicked
def drawPotentialMoves(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        #sqSelected is a piece that can be moved
        if gs.whiteToMove == True:
            colour = "w"
        else:
            colour = "b"
        if gs.board[r][c][0] == colour:
            p.draw.rect(screen, "green", p.Rect(c*SQ_SIZE+404,r*SQ_SIZE+137,SQ_SIZE,SQ_SIZE), width=2)                                       
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    p.draw.rect(screen, "red", p.Rect(SQ_SIZE*move.endCol+404,SQ_SIZE*move.endRow+137,SQ_SIZE,SQ_SIZE), width=2)
                    

def drawResultText(screen, gs, timerRunOut, userText1, userText2):
    #Draws checkmate if someone is in checkmate
    if gs.checkMate:
        if gs.winner == "White":
            winnerName = userText1
        else: 
            winnerName = userText2
        message = ("Checkmate! "+winnerName+" wins!")
        font = p.font.Font('freesansbold.ttf', 20)
        text = font.render(message, True, "red3", "gray15")
        textRect = text.get_rect()
        textRect.center = (685,29)
        screen.blit(text, textRect)
    #Draws stalemate if the game is in stalemate
    
    elif gs.staleMate:
        winnerName = "No winner"
        message = ("Stalemate!")
        font = p.font.Font('freesansbold.ttf', 20)
        text = font.render(message, True, "red3", "gray15")
        textRect = text.get_rect()
        textRect.center = (685,29)
        screen.blit(text, textRect)
    #Draws that the timer has run out if someone's timer has run out
    elif timerRunOut:
        if gs.winner == "White":
            winnerName = userText1
        else: 
            winnerName = userText2
        message = ("Time has run out! "+winnerName+" wins!")
        font = p.font.Font('freesansbold.ttf', 20)
        text = font.render(message, True, "red3", "gray15")
        textRect = text.get_rect()
        textRect.center = (685,29)
        screen.blit(text, textRect)

def drawCheckText(screen, gs):
    print(gs.check)
    if gs.check == True:
        #Draw the check text onto the screen
        message = ("Check!")
        font = p.font.Font('freesansbold.ttf', 20)
        text = font.render(message, True, "red3", "gray15")
        textRect = text.get_rect()
        textRect.center = (685,29)
        screen.blit(text, textRect)
    #Remove the check text off the screen
    elif gs.check == False:
        message = ("Check!")
        font = p.font.Font('freesansbold.ttf', 20)
        text = font.render(message, True, "gray25", "gray25")
        textRect = text.get_rect()
        textRect.center = (685,29)
        screen.blit(text, textRect)



def clearResultText(screen, gs):
    if gs.moveUndone or gs.check == False:
        font = p.font.Font('freesansbold.ttf', 20)
        text = font.render("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", True, "gray25", "gray25")
        textRect = text.get_rect()
        textRect.center = (685,29)
        screen.blit(text, textRect)

def drawPieceValues(screen, gs):
    pieceValues = p.transform.scale(p.image.load("Piece Values.png"), (255, 324))
    screen.blit(pieceValues, (25, 136))

def drawBlackScore(screen, gs):
    whiteScore = p.transform.scale(p.image.load("Black Score Difference.png"), (235, 127))
    screen.blit(whiteScore, (1049, 136))


def drawWhiteScore(screen, gs):
    whiteScore = p.transform.scale(p.image.load("White Score Difference.png"), (235, 127))
    screen.blit(whiteScore, (1049, 565))

#Draws the score difference to the side of the board
def drawScoreDifference(screen, capturedPieces):
    #Initialises the variables
    bPnum = 0
    bBnum = 0
    bNnum = 0
    bRnum = 0
    bQnum = 0
    wPnum = 0
    wBnum = 0
    wNnum = 0
    wRnum = 0
    wQnum = 0
    font = p.font.Font('freesansbold.ttf', 20)
    for piece in capturedPieces: #Goes through the captured pieces list and adds up how many of each piece is there
        if piece == "bP":
            bPnum = int(bPnum) #Ensures the variable is an integer before continuing.
            bPnum +=1 #Adds 1 to the variable
            bPnum = str(bPnum) #Changes the variable back to a string
            #Draws that number to the screen
            text = font.render(bPnum, True,"black",(186,186,186))
            textRect = text.get_rect()
            textRect.center = (1068,622)
            screen.blit(text, textRect)
        if piece == "bB":
            bBnum = int(bBnum) #Ensures the variable is an integer before continuing.
            bBnum +=1 #Adds 1 to the variable
            bBnum = str(bBnum) #Changes the variable back to a string
            #Draws that number to the screen
            text = font.render(bBnum, True,"black",(186,186,186))
            textRect = text.get_rect()
            textRect.center = (1111,622)
            screen.blit(text, textRect)
        if piece == "bN":
            bNnum = int(bNnum) #Ensures the variable is an integer before continuing.
            bNnum +=1 #Adds 1 to the variable
            bNnum = str(bNnum) #Changes the variable back to a string
            #Draws that number to the screen
            text = font.render(bNnum, True,"black",(186,186,186))
            textRect = text.get_rect()
            textRect.center = (1160,622)
            screen.blit(text, textRect)
        if piece == "bR":
            bRnum = int(bRnum) #Ensures the variable is an integer before continuing.
            bRnum +=1 #Adds 1 to the variable
            bRnum = str(bRnum) #Changes the variable back to a string
            #Draws that number to the screen
            text = font.render(bRnum, True,"black",(186,186,186))
            textRect = text.get_rect()
            textRect.center = (1207,622)
            screen.blit(text, textRect)
        if piece == "bQ":
            bQnum = int(bQnum) #Ensures the variable is an integer before continuing.
            bQnum +=1 #Adds 1 to the variable
            bQnum = str(bQnum) #Changes the variable back to a string
            #Draws that number to the screen
            text = font.render(bQnum, True,"black",(186,186,186))
            textRect = text.get_rect()
            textRect.center = (1257,622)
            screen.blit(text, textRect)
        if piece == "wP":
            wPnum = int(wPnum) #Ensures the variable is an integer before continuing.
            wPnum +=1 #Adds 1 to the variable
            wPnum = str(wPnum) #Changes the variable back to a string
            #Draws that number to the screen
            text = font.render(wPnum, True,"black",(186,186,186))
            textRect = text.get_rect()
            textRect.center = (1068,188)
            screen.blit(text, textRect)
        if piece == "wB":
            wBnum = int(wBnum) #Ensures the variable is an integer before continuing.
            wBnum +=1 #Adds 1 to the variable
            wBnum = str(wBnum) #Changes the variable back to a string
            #Draws that number to the screen
            text = font.render(wBnum, True,"black",(186,186,186))
            textRect = text.get_rect()
            textRect.center = (1111,188)
            screen.blit(text, textRect)
        if piece == "wN":
            wNnum = int(wNnum) #Ensures the variable is an integer before continuing.
            wNnum +=1 #Adds 1 to the variable
            wNnum = str(wNnum) #Changes the variable back to a string
            #Draws that number to the screen
            text = font.render(wNnum, True,"black",(186,186,186))
            textRect = text.get_rect()
            textRect.center = (1160,188)
            screen.blit(text, textRect)
        if piece == "wR":
            wRnum = int(wRnum) #Ensures the variable is an integer before continuing.
            wRnum +=1 #Adds 1 to the variable
            wRnum = str(wRnum) #Changes the variable back to a string
            #Draws that number to the screen
            text = font.render(wRnum, True,"black",(186,186,186))
            textRect = text.get_rect()
            textRect.center = (1207,188)
            screen.blit(text, textRect)
        if piece == "wQ":
            wQnum = int(wQnum) #Ensures the variable is an integer before continuing.
            wQnum +=1 #Adds 1 to the variable
            wQnum = str(wQnum) #Changes the variable back to a string
            #Draws that number to the screen
            text = font.render(wQnum, True,"black",(186,186,186))
            textRect = text.get_rect()
            textRect.center = (1257,188)
            screen.blit(text, textRect)
        #Reassign all variables to integers to be used in calculations
        bPnum = int(bPnum)
        bBnum = int(bBnum)
        bNnum = int(bNnum)
        bRnum = int(bRnum)
        bQnum = int(bQnum)
        wPnum = int(wPnum)
        wBnum = int(wBnum)
        wNnum = int(wNnum)
        wRnum = int(wRnum)
        wQnum = int(wQnum)

        #Clear previous white score difference (For a cleaner look on the screen)
        text = font.render("999", True,(186,186,186),(186,186,186))
        textRect = text.get_rect()
        textRect.center = (1165,676)
        screen.blit(text, textRect)

        #Calculate and display white's score difference
        whiteScoreDiff = (bPnum + bBnum*3 + bNnum*3 + bRnum*5 + bQnum*9) - (wPnum + wBnum*3 + wNnum*3 + wRnum*5 + wQnum*9)
        if whiteScoreDiff > 0: #Changes the format when the number is above zero to have a + before the number
            whiteScoreDiff = "+"+str(whiteScoreDiff)
        whiteScoreDiff = str(whiteScoreDiff) #Changes the data type back to string
        #Draws the score difference onto the screen
        text = font.render(whiteScoreDiff, True,"black",(186,186,186))
        textRect = text.get_rect()
        textRect.center = (1165,676)
        screen.blit(text, textRect)

        #Clear previous black score difference (For a cleaner look on the screen)
        text = font.render("999", True,(186,186,186),(186,186,186))
        textRect = text.get_rect()
        textRect.center = (1165,237)
        screen.blit(text, textRect)

        #Calculate and display black's score difference
        blackScoreDiff = (wPnum + wBnum*3 + wNnum*3 + wRnum*5 + wQnum*9) - (bPnum + bBnum*3 + bNnum*3 + bRnum*5 + bQnum*9)
        if blackScoreDiff > 0: #Changes the format when the number is above zero to have a + before the number
            blackScoreDiff = "+"+str(blackScoreDiff)
        blackScoreDiff = str(blackScoreDiff) #Changes the data type back to string
        #Draws the score difference onto the screen
        text = font.render(blackScoreDiff, True,"black",(186,186,186))
        textRect = text.get_rect()
        textRect.center = (1165,237)
        screen.blit(text, textRect)

def whiteTime(screen, counterW):
    minsW, secsW = divmod(counterW, 60)
    timeformatW = '{:02d}:{:02d}'.format(minsW, secsW) #Puts the seconds into the correct format
    font = p.font.Font('freesansbold.ttf', 30) #Assigns the font
    #Draws the timer to the screen
    if counterW > 1800:
        timeformatW = "--:--"
    text = font.render(timeformatW, True, "white", "gray15")
    textRect = text.get_rect()
    textRect.center = (918,759)
    screen.blit(text, textRect)

def blackTime(screen, counterB):
    minsB, secsB = divmod(counterB, 60)
    timeformatB = '{:02d}:{:02d}'.format(minsB, secsB) #Puts the seconds into the correct format
    font = p.font.Font('freesansbold.ttf', 30) #Assigns the font
    #Draws the timer to the screen
    if counterB > 1800:
        timeformatB = "--:--"
    text = font.render(timeformatB, True, "white", "gray15")
    textRect = text.get_rect()
    textRect.center = (918,103)
    screen.blit(text, textRect)

#Draws player 1's username to the screen
def drawPlayer1(screen, userText1):
    font = p.font.Font('freesansbold.ttf', 30) #Assigns the font
    text = font.render(userText1, True, "white", "gray15")
    textRect = text.get_rect()
    textRect.center = (444,759)
    screen.blit(text, textRect)

#Draws player 2's username to the screen
def drawPlayer2(screen, userText2):
    font = p.font.Font('freesansbold.ttf', 30) #Assigns the font
    text = font.render(userText2, True, "white", "gray15")
    textRect = text.get_rect()
    textRect.center = (444,103)
    screen.blit(text, textRect)


#----------------------------------------------------#
#--------------------Main Menu-----------------------#
#----------------------------------------------------#

SCREEN_HEIGHT = 862
SCREEN_WIDTH = 1368


#Button class
class Button():
    def __init__(self, x, y, image, scale):
        width = image.get_width()
        height = image.get_height()
        self.image = p.transform.scale(image, (int(width*scale), int(height*scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False

    def draw(self, menuScreen):
        action = ""
        #Get mouse position
        pos = p.mouse.get_pos()
        #Check mouseover and clicked conditions
        if self.rect.collidepoint(pos):
            if p.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                action = "Click"
            if p.mouse.get_pressed()[0] == 0:
                self.clicked = False
            if self.clicked == False:
                action = "Hover"

        #draw button to screen
        menuScreen.blit(self.image, (self.rect.x, self.rect.y))

        return action



def mainMenu():
    p.init()
    clock = p.time.Clock()
    menuScreen = p.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))

    #Loads the images
    play_img = p.image.load("Play Button.png").convert_alpha()
    leaderboard_img = p.image.load("Leaderboard Button.png").convert_alpha()
    oneMin_img = p.image.load("1 Min Button.png").convert_alpha()
    threeMin_img = p.image.load("3 Min Button.png").convert_alpha()
    fiveMin_img = p.image.load("5 Min Button.png").convert_alpha()
    tenMin_img = p.image.load("10 Min Button.png").convert_alpha()
    thirtyMin_img = p.image.load("30 Min Button.png").convert_alpha()
    infinite_img = p.image.load("Infinite Button.png").convert_alpha()

    #Initialises the buttons
    play_button = Button(464, 270, play_img, 0.5)
    leaderboard_button = Button(990, 30, leaderboard_img, 0.5)
    oneMin_button = Button(65, 235, oneMin_img, 0.5)
    infinite_button = Button(237, 235, infinite_img, 0.5)
    threeMin_button = Button(65, 325, threeMin_img, 0.5)
    fiveMin_button = Button(237, 325, fiveMin_img, 0.5)
    tenMin_button = Button(65, 425, tenMin_img, 0.5)
    thirtyMin_button = Button(237, 425, thirtyMin_img, 0.5)
    

    p.display.set_caption("Main Menu")
    running = True
    t=0
    global userText1
    global userText2
    userText1 = ""
    userText2 = ""
    font = p.font.Font('freesansbold.ttf', 25)
  
    #Creates rectangles
    player1Box = p.Rect(131, 43, 240, 30)
    player2Box = p.Rect(131, 90, 400, 30)
  
    #colorActive stores the colour black which becomes active when the box is clicked
    colorActive = p.Color('black')
  
    #colorPassive stores the colour dark blue which is the colour of the box
    colorPassive = p.Color(5,5,66)
    color1 = colorPassive
    color2 = colorPassive
    active1 = False
    active2 = False
    #Main loop
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            if e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() #(x,y) location of mouse
                print(location)
                if player1Box.collidepoint(e.pos):
                    active1 = True
                else:
                    active1 = False
                if player2Box.collidepoint(e.pos):
                    active2 = True
                else:
                    active2 = False

            if e.type == p.KEYDOWN:
                # Check for backspace
                if active1 == True:
                    if e.key == p.K_BACKSPACE:
                        # get text input from 0 to -1 i.e. end.
                        userText1 = userText1[:-1]
  
                    # Unicode standard is used for string
                    # formation
                    else:
                        if len(userText1) <=12:
                            userText1 += e.unicode
                elif active2 == True:
                    if e.key == p.K_BACKSPACE:
                        # get text input from 0 to -1 i.e. end.
                        userText2 = userText2[:-1]
  
                    # Unicode standard is used for string
                    # formation
                    else:
                        if len(userText2) <=12:
                            userText2 += e.unicode
        if active1:
            color1 = colorActive
        else:
            color1 = colorPassive
        if active2:
            color2 = colorActive
        else:
            color2 = colorPassive
          
        # draw rectangle and argument passed which should be on screen
        p.draw.rect(menuScreen, color1, player1Box)
        p.draw.rect(menuScreen, color2, player2Box)
  
        textSurface1 = font.render(userText1, True, (255, 255, 255))
        textSurface2 = font.render(userText2, True, (255, 255, 255))
      
        # render at position stated in arguments
        menuScreen.blit(textSurface1, (player1Box.x+5, player1Box.y+5))
        menuScreen.blit(textSurface2, (player2Box.x+5, player2Box.y+5))
      
        # set width of textfield so that text cannot get
        # outside of user's text input
        player1Box.w = max(240, textSurface1.get_width()+10)
        player2Box.w = max(240, textSurface2.get_width()+10)
      
        # display.flip() will update only a portion of the
        # screen to updated, not full area
        p.display.flip()
      
        # clock.tick(60) means that for every second at most
        # 60 frames should be passed.
        clock.tick(60)
        drawBackground(menuScreen)
        
        

        if play_button.draw(menuScreen) == "Click": #Whether the play button has been clicked
            if t !=0 and len(userText1) !=0 and len(userText2) !=0:
                running = False
                main(t, userText1, userText2)
        if play_button.draw(menuScreen) == "Hover": #Whether the mouse cursor is over the play button
            p.draw.rect(menuScreen, "green", p.Rect(464, 270, play_img.get_width()/2 -8, play_img.get_height()/2 - 8), 2)
        if leaderboard_button.draw(menuScreen) == "Click": #Whether the leaderboard button has been clicked
            p.draw.rect(menuScreen, "red", p.Rect(990, 30, leaderboard_img.get_width()/2 -8, leaderboard_img.get_height()/2 - 8), 2)
            leaderboard()
            print("Leaderboard")
        if leaderboard_button.draw(menuScreen) == "Hover": #Whether the mouse cursor is over the leaderboard button
            p.draw.rect(menuScreen, "green", p.Rect(990, 30, leaderboard_img.get_width()/2 -8, leaderboard_img.get_height()/2 - 8), 2)
        if oneMin_button.draw(menuScreen) == "Click": #Whether the one minute button has been clicked
            t = 60
            print("1 Minute")
        if oneMin_button.draw(menuScreen) == "Hover": #Whether the mouse cursor is over the one minute button
            p.draw.rect(menuScreen, "green", p.Rect(65, 235, oneMin_img.get_width()/2 -8, oneMin_img.get_height()/2 - 8), 2)
        if infinite_button.draw(menuScreen) == "Click": #Whether the infinite button has been clicked
            print("Infinite Time")
            t = 9999
        if infinite_button.draw(menuScreen) == "Hover": #Whether the mouse cursor is over the infinite button
            p.draw.rect(menuScreen, "green", p.Rect(237, 235, infinite_img.get_width()/2 -2, infinite_img.get_height()/2 - 2), 2)
        if threeMin_button.draw(menuScreen) == "Click": #Whether the three minute button has been clicked
            t = 180
            print("3 Minutes")
        if threeMin_button.draw(menuScreen) == "Hover": #Whether the mouse cursor is over the three minute button
            p.draw.rect(menuScreen, "green", p.Rect(65, 325, threeMin_img.get_width()/2 -8, threeMin_img.get_height()/2 - 8), 2)
        if fiveMin_button.draw(menuScreen) == "Click": #Whether the five minute button has been clicked
            t = 300
            print("5 Minutes")
        if fiveMin_button.draw(menuScreen) == "Hover": #Whether the mouse cursor is over the five minute button
            p.draw.rect(menuScreen, "green", p.Rect(237, 325, fiveMin_img.get_width()/2 -8, fiveMin_img.get_height()/2 - 8), 2)
        if tenMin_button.draw(menuScreen) == "Click": #Whether the ten minute button has been clicked
            t = 600
            print("10 Minutes")
        if tenMin_button.draw(menuScreen) == "Hover": #Whether the mouse cursor is over the ten minute button
            p.draw.rect(menuScreen, "green", p.Rect(65, 425, tenMin_img.get_width()/2 -8, tenMin_img.get_height()/2 - 8), 2)
        if thirtyMin_button.draw(menuScreen) == "Click": #Whether the thirty button has been clicked
            t = 1800
            print("30 Minutes")
        if thirtyMin_button.draw(menuScreen) == "Hover": #Whether the mouse cursor is over the thirty minute button
            p.draw.rect(menuScreen, "green", p.Rect(237, 425, tenMin_img.get_width()/2 -8, tenMin_img.get_height()/2 - 8), 2)        
        p.display.flip()

#Draws the background to the screen
def drawBackground(menuScreen):
    image = p.transform.scale(p.image.load("Main Menu with Time Controls and Input Boxes.png"), (SCREEN_WIDTH,SCREEN_HEIGHT)) #Loads the image and transforms it to the screen size
    menuScreen.blit(image, p.Rect(0,0,SCREEN_WIDTH,SCREEN_HEIGHT)) #Draws it to the screen


#----------------------------------------------------#
#--------------------Database------------------------#
#----------------------------------------------------#

def Database(userText1, userText2, winnerName):
    #Connects to the database
    conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\Silen\OneDrive\Documents\A-Levels\Computer Science\NEA\Chess_Game\Leaderboard.accdb;')
    cursor = conn.cursor()
    #Selects everything from the leaderboard
    cursor.execute("SELECT * FROM Leaderboard")

    #Stores everything in the leaderboard as a list
    list = cursor.fetchall()
    print(list)
    usernames = []
    #Stores all usernames in the list called usernames
    for items in list:
        for item in items:
            if isinstance(item, str) == True:
                usernames.append(item)

    newPlayer1 = True
    newPlayer2 = True
    #Determines whether the users are new players
    for name in usernames:
        if name == userText1:
            newPlayer1 = False
        if name == userText2:
            newPlayer2 = False

    #Calculations for if player 1 is already in the leaderboard
    if newPlayer1 == False:
        cursor.execute("SELECT * FROM Leaderboard WHERE Username ="+"'"+userText1+"'")
        player1Stats = cursor.fetchall() #Structure is [(ID, GamesPlayed, Wins, Losses, Username, WinPercentage, Draws)]
        if winnerName == userText1:
            player1Stats[0][2] += 1
        if winnerName == "No winner":
            player1Stats[0][6] += 1
        if winnerName == userText2:
            player1Stats[0][3] += 1
        player1Stats[0][1] += 1
        #Updates the database with new values
        cursor.execute("UPDATE Leaderboard SET GamesPlayed="+str(player1Stats[0][1])+", Wins="+str(player1Stats[0][2])
                       +", Losses="+str(player1Stats[0][3])+", Draws="+str(player1Stats[0][6])+" WHERE Username="+"'"+userText1+"'")
        cursor.commit()

    #Calculations for if player 1 is a new player   
    else:
        player1Stats = [[0, 0, 0, userText1, 0]]
        if winnerName == userText1:
            player1Stats[0][1] += 1
        if winnerName == "No winner":
            player1Stats[0][4] += 1
        if winnerName == userText2:
            player1Stats[0][2] += 1
        player1Stats[0][0] += 1
        #Updates the database with new values
        cursor.execute("INSERT INTO Leaderboard(GamesPlayed, Wins, Losses, Username, Draws) VALUES"+str(tuple(player1Stats[0])))
        cursor.commit()
    

    #Calculations for if player 2 is already in the leaderboard
    if newPlayer2 == False:
        cursor.execute("SELECT * FROM Leaderboard WHERE Username ="+"'"+userText2+"'")
        player2Stats = cursor.fetchall() #Structure is [(ID, GamesPlayed, Wins, Losses, Username, WinPercentage, Draws)]

        if winnerName == userText2:
            player2Stats[0][2] += 1
        if winnerName == "No winner":
            player2Stats[0][6] += 1
        if winnerName == userText1:
            player2Stats[0][3] += 1
        player2Stats[0][1] += 1
       
        #Updates the database with new values
        cursor.execute("UPDATE Leaderboard SET GamesPlayed="+str(player2Stats[0][1])+", Wins="+str(player2Stats[0][2])
                       +", Losses="+str(player2Stats[0][3])+", Draws="+str(player2Stats[0][6])+" WHERE Username="+"'"+userText2+"'")
        cursor.commit()
    
    #Calculations for if player 2 is a new player
    else:
        player2Stats = [[0, 0, 0, userText2, 0]]

        if winnerName == userText2:
            player2Stats[0][1] += 1
        if winnerName == "No winner":
            player2Stats[0][4] += 1
        if winnerName == userText1:
            player2Stats[0][2] += 1
        player2Stats[0][0] += 1
        #Updates the database with new values
        cursor.execute("INSERT INTO Leaderboard(GamesPlayed, Wins, Losses, Username, Draws) VALUES"+str(tuple(player2Stats[0])))
        cursor.commit()

    #Selects all the new updated database values
    cursor.execute("SELECT * FROM Leaderboard")
    newList = cursor.fetchall()
    sortedList = sorted(newList, key=itemgetter(5), reverse=True) #Sorts the database by win percentage
    print(sortedList)

    

#-------------------------------------------------------#
#--------------------Leaderboard------------------------#
#-------------------------------------------------------#

def leaderboard():
    #Connects to the database
    conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\Silen\OneDrive\Documents\A-Levels\Computer Science\NEA\Chess_Game\Leaderboard.accdb;')
    cursor = conn.cursor()
    #Selects all the new updated database values
    cursor.execute("SELECT * FROM Leaderboard")
    newList = cursor.fetchall()
    sortedList = sorted(newList, key=itemgetter(5), reverse=True) #Sorts the database by win percentage
    print(sortedList)

    lWindow = tk.Tk()
    lWindow.title("Leaderboard")
    lWindow.geometry("1368x862")
    tree = ttk.Treeview(lWindow)
    #clam, alt, default, classic, vista, xpnative
    tree["show"] = "headings" #Removes the blank column at the beginning

    s = ttk.Style(lWindow)
    s.theme_use("alt")
    s.configure('Treeview', rowheight=40)
    s.configure(".", font=("freesansbold.ttf",25))
    s.configure("Treeview.Heading", font=("freesansbold.ttf",25, "bold"))

    #Define the columns
    tree["columns"] = ("Position","Username","GamesPlayed","Wins","Losses","Draws","WinPercentage")

    #Assign the width, minwidth and anchor to the respective columns
    tree.column("Position", width=135, minwidth=135, anchor=tk.CENTER)
    tree.column("Username", width=315, minwidth=315, anchor=tk.CENTER)
    tree.column("GamesPlayed", width=280, minwidth=280, anchor=tk.CENTER)
    tree.column("Wins", width=110, minwidth=110, anchor=tk.CENTER)
    tree.column("Losses", width=130, minwidth=130, anchor=tk.CENTER)
    tree.column("Draws", width=105, minwidth=105, anchor=tk.CENTER)
    tree.column("WinPercentage", width=300, minwidth=300, anchor=tk.CENTER)

    #Assign the heading names to the respective columns
    tree.heading("Position", text="Position", anchor=tk.CENTER)
    tree.heading("Username", text="Username", anchor=tk.CENTER)
    tree.heading("GamesPlayed", text="Games Played", anchor=tk.CENTER)
    tree.heading("Wins", text="Wins", anchor=tk.CENTER)
    tree.heading("Losses", text="Losses", anchor=tk.CENTER)
    tree.heading("Draws", text="Draws", anchor=tk.CENTER)
    tree.heading("WinPercentage", text="Win Percentage", anchor=tk.CENTER)

    i=0
    pos = 1
    for row in sortedList:
        tree.insert("", i, text="", values=(pos, row[4], row[1], row[2], row[3], row[6], str(round(row[5],1))+"%"))
        i += 1
        pos += 1

    hsb = ttk.Scrollbar(lWindow, orient="vertical")
    hsb.configure(command=tree.yview)
    tree.configure(yscrollcommand=hsb.set)
    hsb.pack(fill=Y, side=RIGHT)
    tree.pack(fill=BOTH,expand=1)
    lWindow.mainloop()

if __name__ == "__main__":
    mainMenu()







