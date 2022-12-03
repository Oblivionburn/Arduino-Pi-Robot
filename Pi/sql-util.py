import sqlite3
from os.path import exists

new_tables = """
    --List of motors available
    CREATE TABLE Motors
    (
        ID INTEGER PRIMARY KEY,
        Name TEXT --name of the motor for Arduino (e.g. motor00, motor01, motor02)
    );

    --List of single movements
    CREATE TABLE Moves
    (
        ID INTEGER PRIMARY KEY,
        TimeStamp TEXT, --date/time the move happened
        Motor_ID INTEGER, --motor moved
        Degree INTEGER, --degree/angle motor was moved to (e.g. 45, 90, 180)
        Image_ID INTEGER, --image snapped at the end of the move
        FOREIGN KEY (Motor_ID) REFERENCES Motors (ID),
        FOREIGN KEY (Image_ID) REFERENCES Images (ID)
    );
    CREATE INDEX IDX_Moves ON Moves (Motor_ID, Degree);

    --List of series of movements
    CREATE TABLE MoveSets
    (
        ID INTEGER PRIMARY KEY,
        MoveSet_ID INTEGER,
        Move_ID INTEGER,
        FOREIGN KEY (Move_ID) REFERENCES Moves (ID)
    );
    CREATE INDEX IDX_MoveSets ON MoveSets (MoveSet_ID, Move_ID);

    --List of series of movements that were executed
    CREATE TABLE MovesMade
    (
        ID INTEGER PRIMARY KEY,
        StartTime TEXT, --time we started executing the series of moves
        EndTime TEXT, --time we finished executing the series of moves
        MoveSet_ID INTEGER, --the moves executed
        FOREIGN KEY (MoveSet_ID) REFERENCES MoveSets (MoveSet_ID),
    );

    --List of images
    CREATE TABLE Images
    (
        ID INTEGER PRIMARY KEY,
        TimeStamp TEXT,
        Image BLOB --color data = {{255, 255, 255, 255}, {255, 255, 255, 255}}
    );

    --List of learned patterns (e.g. I did X and Y happened)
    CREATE TABLE Patterns
    (
        ID INTEGER PRIMARY KEY,
        TimeStamp TEXT,
        Moves_ID INTEGER, --the move executed with resulting image
        Image_ID INTEGER, --the image compared against
        Difference BLOB, --color data difference between the images = {{255, 255, 255, 255}, {255, 255, 255, 255}}
        FOREIGN KEY (Moves_ID) REFERENCES Moves (ID),
        FOREIGN KEY (Image_ID) REFERENCES Images (ID)
    )
"""

def GetConnection():
    #connect function creates the database if it doesn't exist
    return sqlite3.connect("brain.db")

def Init():
    new_brain = False

    #check if the database exists first, so we know if we need to create the tables or not
    if not exists("brain.db"):
        new_brain = True

    conn = GetConnection()

    if new_brain:
        try:
            with conn:
                conn.execute(new_tables)
        except sqlite3.Error as err:
            print('SQLite error: %s' % (' '.join(err.args)))

    conn.close()

def ExecuteScalar(sql, parameters):
    conn = GetConnection()
    result = None

    try:
        with conn:
            result = conn.execute(sql, parameters)
    except sqlite3.Error as err:
        print('SQLite error: %s' % (' '.join(err.args)))

    conn.close()
    return result.fetchall()

def ExecuteNonScalar(sql, data):
    conn = GetConnection()

    try:
        with conn:
            conn.execute(sql, data)
    except sqlite3.Error as err:
        print('SQLite error: %s' % (' '.join(err.args)))

    conn.close()