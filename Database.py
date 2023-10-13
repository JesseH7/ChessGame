import pyodbc

def Database(SQLStatement):
    conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=C:\Users\Silen\OneDrive\Documents\A-Levels\Computer Science\NEA\Chess_Game\Leaderboard.accdb;')
    cursor = conn.cursor()
    cursor.execute(SQLStatement)

    list = cursor.fetchall()
    print(list)


