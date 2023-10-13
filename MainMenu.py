#-------------------------------------------------------------------------------
#Main menu file, which will be responsible for introducing the game to the user
#-------------------------------------------------------------------------------

import pygame as p
import ChessMain
import time


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
    #Main loop
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() #(x,y) location of mouse
                print(location)
        drawBackground(menuScreen)
        if play_button.draw(menuScreen) == "Click": #Whether the play button has been clicked
            running = False
        if play_button.draw(menuScreen) == "Hover": #Whether the mouse cursor is over the play button
            p.draw.rect(menuScreen, "green", p.Rect(464, 270, play_img.get_width()/2 -8, play_img.get_height()/2 - 8), 2)
        if leaderboard_button.draw(menuScreen) == "Click": #Whether the leaderboard button has been clicked
            p.draw.rect(menuScreen, "red", p.Rect(990, 30, leaderboard_img.get_width()/2 -8, leaderboard_img.get_height()/2 - 8), 2)
            print("Leaderboard")
        if leaderboard_button.draw(menuScreen) == "Hover": #Whether the mouse cursor is over the leaderboard button
            p.draw.rect(menuScreen, "green", p.Rect(990, 30, leaderboard_img.get_width()/2 -8, leaderboard_img.get_height()/2 - 8), 2)
        if oneMin_button.draw(menuScreen) == "Click": #Whether the one minute button has been clicked
            t = 60
            print("1 Minute")
        if oneMin_button.draw(menuScreen) == "Hover": #Whether the mouse cursor is over the one minute button
            p.draw.rect(menuScreen, "green", p.Rect(65, 235, oneMin_img.get_width()/2 -8, oneMin_img.get_height()/2 - 8), 2)
        if infinite_button.draw(menuScreen) == "Click": #Whether the infinite button has been clicked
            infinite = True
            print("Infinite Time")
        infinite = False
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


print(p.time.Clock())
mainMenu()

