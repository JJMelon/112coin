# Alexander Penney 2020 

import sqlite3
import time, random, linecache
from dataclasses import make_dataclass
from cmu_112_graphics import *

#create database in memory
database = sqlite3.connect('test.db')

#creates a random transaction as tuple
def createTx():
    current = time.asctime(time.localtime(time.time()))
    amt = random.randint(1, 20)
    lines = 237 #number of lines in our username file
    sender = linecache.getline('usernames.txt', random.randint(1,lines))
    #make sure receiver is not same as sender
    while True:
        receiver = linecache.getline('usernames.txt', random.randint(1,lines))
        if receiver != sender: break
    sender = sender[:-1]
    receiver = receiver[:-1]
    return (sender, receiver, amt, current)

#returns list of n random transactions
def makeTxs(n):
    txs = []
    for tx in range(n):
        txs.append(createTx())
    return txs

def makeInitialTable():
    try:
        database = sqlite3.connect('test.db')
        #initialize our cursor object, which allows us to interact with our created database
        c = database.cursor()
        c.execute('''CREATE TABLE txs (
                        id integer primary key autoincrement,
                        sender text,
                        receiver text,
                        amt integer,
                        time text
                        )''')
    except sqlite3.Error as error:
        print("Sqlite error returned: ", error)
    finally:
        if database:
            database.close()
            print("Database Txs Table Created!")

def insertTx(tx, c):
    sender, receiver, amt, time = tx
    c.execute("INSERT INTO txs (sender, receiver, amt, time) VALUES (?, ?, ?, ?)", (sender, receiver, amt, time))

def getSent(user):
    c.execute("SELECT * FROM txs WHERE sender=?", (user,))
    return c.fetchall()

def getReceived(user):
    c.execute("SELECT * FROM txs WHERE receiver=?", (user,))
    return c.fetchall()

def removeTx(place):
    with database:
        c.execute("DELETE from txs WHERE name=?", (place))

def delTable(table):
    try:
        database = sqlite3.connect('test.db')
        c = database.cursor()
        query = f'DROP TABLE {table}'
        c.execute(query)
        database.commit()
    except sqlite3.Error as error:
        print("Sqlite error returned: ", error)
    finally:
        if database:
            database.close()
            print("The %s was Dropped!"%table)

#returns list of txs from starting index to end index inclusive
def getTxsRange(start, end, c):
    c.execute("SELECT * FROM txs WHERE id >= ? AND id <= ?", (start, end))
    return c.fetchall()

#populate the database with n random transactions
def populate(app, n):
    try:
        database = sqlite3.connect('test.db')
        #initialize our cursor object, which allows us to interact with our created database
        c = database.cursor()
        
        #insert our n # of txs into the database
        for tx in makeTxs(n):
            insertTx(tx, c)

        database.commit() 
        #update our app model with the newly updated database
        c.execute("SELECT * FROM txs")
        app.txs = c.fetchall()
        updateMaxIndex(app, c) 
    except sqlite3.Error as error:
        print("Sqlite error returned: ", error)
    finally:
        if database:
            database.close()
            print("Database closed")

#puts the initial transactions from our db into memory when app is started and
#sets our starting index to 0, assigns current transactions to the first app.txWidth #
def initIndex(app):
    try:
        database = sqlite3.connect('test.db')
        #initialize our cursor object, which allows us to interact with our created database
        c = database.cursor()
        c.execute("SELECT * FROM txs")

        #app model controller
        app.index = 0
        app.txs = c.fetchall()
        app.currTxs = app.txs[0:app.txWidth]
        updateMaxIndex(app, c)
    except sqlite3.Error as error:
        print("Sqlite error returned: ", error)
    finally:
        if database:
            database.close()
            print("Database closed")

def updateMaxIndex(app, c):
    c.execute("SELECT MAX(id) FROM txs")
    app.txCount = c.fetchone()[0]

def appStarted(app):
    app.txWidth = 15
    app.topMargin = 40
    app.sideMargin = 20
    initIndex(app)
    # populate(app, 1000)

def timerFired(app):
    pass

def keyPressed(app, event):
    if event.key == 'Down':
        moveIndex(app, 1)
    elif event.key == 'Up':
        moveIndex(app, -1)
    elif event.key == "p":
        print('populating %d transactions...'%app.txWidth)
        populate(app, app.txWidth)
        dIndex = app.txCount - app.index - app.txWidth
        moveIndex(app, dIndex)
    elif event.key == "s":
        moveIndex(app, -app.index)

def moveIndex(app, dir):
    app.index += dir
    if app.index < 0:
        app.index = 0
    elif app.index > app.txCount - app.txWidth:
        app.index = app.txCount - app.txWidth
    app.currTxs = app.txs[app.index: app.index + app.txWidth]

def redrawAll(app, canvas):
    drawTitle(app, canvas)
    if app.txs != []:
        drawTxs(app, canvas)

def drawTitle(app, canvas):
    canvas.create_text(app.width/2, 2*app.topMargin/3, 
      text="Press Up/Down to change view, P to populate, S to jump to start", 
      font="Arial 10 bold", fill='green')
    canvas.create_text(app.width/2, app.topMargin/4, 
      text="Pending Transactions", 
      font="Arial 14 bold")

def drawTxs(app, canvas):
    txBoxHeight = (app.height-2*app.topMargin)//app.txWidth 
    for i in range(app.txWidth):
        tx = app.currTxs[i]
        x0, y0 = app.sideMargin, app.topMargin + i*txBoxHeight
        drawTx(app, canvas, tx, x0, y0)

def drawTx(app, canvas, tx, x0, y0):
    txBoxHeight = (app.height-2*app.topMargin)//app.txWidth 
    txBoxWidth = app.width - 2*app.sideMargin
    canvas.create_rectangle(x0, y0, x0 + txBoxWidth, y0 + txBoxHeight, width=2)
    txtCy = y0 + txBoxHeight/2
    ID, sender, receiver, amt, time = tx
    canvas.create_text(x0 + app.sideMargin, txtCy, text=(f'{ID}: From: {sender} To: {receiver} -- ${amt} -- %s' %time), 
            font='Arial 10 bold', anchor=W)

# makeInitialTable()

runApp(width=700, height=500)