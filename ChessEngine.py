#--------------------------------------------------------------------------------------------------
#This class is responsible for storing all the information about the current state of a chess game.
#It will also be responsible for determining the valid moves at the current state.
#--------------------------------------------------------------------------------------------------
import pygame as p

class GameState():
    def __init__(self):
        #board is an 8x8 2d list, each element of the list has 2 characters.
        #The first character represents the colour of the piece, "b" or "w".
        #The second character represents the type of piece, "K", "Q", "R", "B", "N" or "P".    
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.check = False
        self.winner = "n/a"
        self.moveUndone = False
        self.enpassantPossible = () #Coordinates for the square where en passant capture is possible
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]

    #Takes a Move as a parameter and excecutes it
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) #Log the move
        self.whiteToMove = not self.whiteToMove #Swap players
        #Update the king's location if moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        #Pawn Promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        #Has the current move put the king in check       
        if (self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])==True) or (self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])==True):
            self.check = True
        else:
            self.check = False

        #En Passant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--" #Capturing the pawn

        #Update enpassantPossible variable
        if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2: #Only on 2 square pawn advances
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()

        #Castling move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #King side castle move
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #Copies the rook to new position
                self.board[move.endRow][move.endCol+1] = "--" #Erase old rook
            else: #Queen side castle move
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] #Copies the rook to new position
                self.board[move.endRow][move.endCol-2] = "--" #Erase old rook

        #Update castling rights whenever it is a rook or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))

    #Undo the last move made
    def undoMove(self):
        if len(self.moveLog) != 0: #To ensure there is a move to undo
            move = self.moveLog.pop()
            self.moveUndone = True
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #Switches the turn back
            #update King's position if needed
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            #Undo en passant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = "--" #Leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            #Undo a 2 square pawn advance
            if move.pieceMoved[1] == "P" and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            #Undo castling rights
            self.castleRightsLog.pop() #Get rid of the new castle rights from the move we are undoing
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs)
            #Undo castling move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: #King side castle
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = "--"
                else: #Queen side castle
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = "--"
    
    #Update castle rights given the move
    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0: #Left white rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7: #Right white rook
                    self.currentCastlingRight.wks = False

        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0: #Left black rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7: #Right black rook
                    self.currentCastlingRight.bks = False



    #All moves considering checks
    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        #1) Generate all possible moves
        moves = self.getAllPossibleMoves()
        #2) For each move, make the move
        for i in range(len(moves)-1, -1, -1): #Going backwards through the list
            self.makeMove(moves[i])
            #3) Generate all opponent's moves, for each of your opponent's moves, see if they attack your king
            self.whiteToMove = not self.whiteToMove #Need to switch again as previous line switches the turn
            if self.inCheck():
                moves.remove(moves[i]) #4) Removes the invalid move of moving a pinned piece
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0: #Either checkmate or stalemate
            if self.inCheck():
                if self.whiteToMove == True:
                    self.winner = "Black"
                else:
                    self.winner = "White"
                self.checkMate = True
            else:
                self.staleMate = True
                self.winner = "No one"
        else:
            self.checkMate = False
            self.staleMate = False

        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastleRights
        return moves

    
    
    #Determine if the current player is in check
    def inCheck(self):
        if self.whiteToMove: 
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])
    
    #Determine if the enemy can attack the square (r,c)
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove #Switch to opponent's turn
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: #Square is under attack by opponent 
                return True
        return False
        

    #All moves without considering checks
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): #Number of rows
            for c in range(len(self.board[r])): #Numer of columns in a given row
                turn = self.board[r][c][0] #finds the first letter of each item (the colour of the piece)
                if (turn == "w" and self.whiteToMove) or (turn == "b" and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    if piece == "P": #Calls the appropriate move function based on piece type
                        self.getPawnMoves(r, c, moves)
                    if piece == "R":
                        self.getRookMoves(r, c, moves)
                    if piece == "B":
                        self.getBishopMoves(r, c, moves)
                    if piece == "Q":
                        self.getQueenMoves(r, c, moves)
                    if piece == "K":
                        self.getKingMoves(r, c, moves)
                    if piece == "N":
                        self.getKnightMoves(r, c, moves)
        return moves

    #Get all Pawn moves for the pawn located at row, column and add these moves to the list
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove == True: #white pawn moves
            if self.board[r-1][c] == "--": #1 square pawn advance
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--": #2 square pawn advance only on row 6 (starting row)
                    moves.append(Move((r, c), (r-2, c), self.board))

            if c-1 >= 0: #Captures to the left
                if self.board[r-1][c-1][0] == "b": #Enemy piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, isEnpassantMove=True))

            if c+1 <= 7: #Captures to the right
                if self.board[r-1][c+1][0] == "b":
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, isEnpassantMove=True))

        else: #Black pawn moves            
            if self.board[r+1][c] == "--": #1 square pawn advance
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--": #2 square pawn advance only on row 1 (starting row)
                    moves.append(Move((r, c), (r+2, c), self.board))

            if c-1 >= 0: #Captures to the left
                if self.board[r+1][c-1][0] == "w":
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c-1), self.board, isEnpassantMove=True))

            if c+1 <= 7: #Captures to the right
                if self.board[r+1][c+1][0] == "w":
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r+1, c+1), self.board, isEnpassantMove=True))
               
    #Get all Rook moves for the pawn located at row, column and add these moves to the list
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) #Up, left, down, right
        if self.whiteToMove == True:
            enemyColour = "b"
        else:
            enemyColour = "w"
        for d in directions:
            for i in range(1,8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7: #On the board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": #Moving into an empty space is valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColour: #Capturing an enemy piece is valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: #It's a ally piece
                        break
                else: #It's off the board
                    break

    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, 1), (1, -1)) #Diagonally: UPLEFT, UPRIGHT, DOWNRIGHT, DOWNLEFT
        if self.whiteToMove == True:
            enemyColour = "b"
        else:
            enemyColour = "w"
        for d in directions:
            for i in range(1,8): #Bishop can move max 7 squares
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7: #On the board
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": #Moving into an empty space is valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColour: #Capturing an enemy piece is valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: #It's a ally piece
                        break
                else: #It's off the board
                    break
    
    #Get all Queen moves for the pawn located at row, column and add these moves to the list
    def getQueenMoves(self, r, c, moves):
        self.getBishopMoves(r, c, moves)
        self.getRookMoves(r, c, moves)

    #Get all Knight moves for the pawn located at row, column and add these moves to the list
    def getKnightMoves(self, r, c, moves):
        directions = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)) #All L shape moves
        if self.whiteToMove == True:
            enemyColour = "b"
        else:
            enemyColour = "w"
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7: #On the board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColour:
                    moves.append(Move((r, c), (endRow, endCol), self.board))
                if endPiece == "--":
                    moves.append(Move((r, c), (endRow, endCol), self.board))

                    

    #Get all King moves for the pawn located at row, column and add these moves to the list
    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)) #King moves 1 square in any direction
        if self.whiteToMove == True:
            allyColour = "w"
        else:
            allyColour = "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7: #On the board
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColour: #Not an ally piece (empty space or enemy piece)
                    moves.append(Move((r, c), (endRow, endCol), self.board))


    #Generate all valid castle moves for the king at (r, c) and add them to the list of moves

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return #Cannot castle while in check
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--": #Is the 2 squares to the right empty
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2): #Is the 2 squares to the right under attack
                moves.append(Move((r,c), (r, c+2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[r][c-3] == "--": #Is the 3 left squares in between the rook and king empty
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2): #Is the 2 left squares under attack
                moves.append(Move((r,c), (r, c-2), self.board, isCastleMove=True))



class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    #Dictionary to map keys to values
    #key:value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                  "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol #ID 0002 would mean a move from (0,0) to (0,2)
        #Pawn promotion
        self.isPawnPromotion = False
        if (self.pieceMoved == "wP" and self.endRow == 0) or (self.pieceMoved == "bP" and self.endRow == 7):
            self.isPawnPromotion = True
        #En Passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            if self.pieceMoved == "bP":
                self.pieceCaptured = "wP"
            else:
                self.pieceCaptured = "bP"
        #Castling move
        self.isCastleMove = isCastleMove

    #Overriding the equals method
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]