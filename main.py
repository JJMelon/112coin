# Alexander Penney 2020 

import sqlite3, json
import time, random, linecache
from dataclasses import make_dataclass
from cmu_112_graphics import *
from hashlib import sha256

# sql Functions
from sqlcalls import *

# blockchain functions
from blockchain import *
from blockchain import BlockChain, Block, Tx, 

#create databases in memory
chainDB = sqlite3.connect('chain.db') # our blockchain JSON strings
txsDB = sqlite3.connect('myTxs.db') #


def appStarted(app):
    app.txWidth = 15
    app.topMargin = 60
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
        print('populating...')
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
    canvas.create_text(x0 + app.sideMargin, txtCy, text=(f'{ID}: From: {sender} To: {receiver} -- ${amt} -- %0.3f' %time), 
            font='Arial 10 bold', anchor=W)

# makeInitialTable()
# runApp(width=700, height=500)