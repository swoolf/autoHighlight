import sqlite3
import os


def main():
    conn = sqlite3.connect('goals.db')
    # initDB(conn)
    # csv2db(conn, 'gifs.csv')
    # printDB(conn)
    printDB(conn)
    print(list_gifs_by_status(conn, 'gif'))
    conn.commit()
    conn.close()

def updateMtIDbyID(conn, ID, mtID):
    c=conn.cursor()
    c.execute('UPDATE goals SET mtID=?, status="mt" WHERE ID=?', (mtID,ID) )
    conn.commit()

def getConn(db):
    if not os.path.isfile(db):
        conn = sqlite3.connect(db)
        initDB(conn)
    else:
        conn = sqlite3.connect(db)
    return conn

def delAll(conn, table):
    c=conn.cursor()
    c.execute('DELETE FROM goals')

def csv2db(conn, fileName):
    c=conn.cursor()
    with open(fileName, 'r') as f:
        for line in f:
            info = line.split(',')
            c.execute("INSERT INTO goals VALUES ('2018-05-16', ? ,'vid1',150,'gif',?,'', '')",(info[0], info[1]) )

def newEntry(conn, date='', ID='', vidID='', time='', status='', url='', mtID='', isGoal=''):
    c=conn.cursor()
    c.execute("INSERT INTO goals VALUES (?,?,?,?,?,?,?,?)",(date, ID, vidID, time, status, url, mtID, isGoal) )
    conn.commit()

def getClips(conn):
    clips=[]
    c=conn.cursor()
    for row in c.execute('SELECT vidID, time FROM goals WHERE status=? AND isGoal=?', ('decided', 'Yes') ):
        clips.append([row[0], row[1]])
    return clips

def list_gifs_by_status(conn, status):
    c=conn.cursor()
    gifs=[]
    for row in c.execute('SELECT ID FROM goals WHERE status=?', (status, )):
        gifs.append(row[0])
    return gifs

def printDB(conn):
    c= conn.cursor()
    for row in c.execute('SELECT * FROM goals ORDER BY ID'):
        print(row)

def initDB(conn):
    c= conn.cursor()
    c.execute('''CREATE TABLE goals
                 (date date, ID text, vidID text, time int, status text, url text, mtID text, isGoal text)''')
    conn.commit()

if __name__ == '__main__':
    main()
