# Alexander Penney 2020 

import sqlite3, json
import time, random, linecache
from dataclasses import make_dataclass
from cmu_112_graphics import *
from hashlib import sha256

# sql Functions
from sqlcalls import *

# keyPress and mousePress handlers:
from handlers import *

# page drawers
from draw import *

# blockchain functions
from blockchain import *

#create databases in memory
chainDB = sqlite3.connect('chain.db') # our blockchain JSON strings
txsDB = sqlite3.connect('myTxs.db') 
''' --- page number guide --- 
       0: Tutorial
       1: Overview
       2: Send
       3: Mint
       4: Recent
       5: View BlockChain'''

def appStarted(app):
    app.txWidth = 15
    app.topMargin = 60
    app.sideMargin = 20
    app.page = 0
    app.pages = ['Tutorial', 'Overview', 'Send', 'Mint', 'Recent', 'View Chain']
    app.userAddress = 'Alby'
    # list of pending transactions in memory
    app.pendingTxs = []
    app.blocks = testBlocks() # TEMP 

    # initialize recent page details
    app.index = 0 # starting index in app.myTxs, will show this tx and following 9 txs
    app.txWidth = 10 # number of transactions viewable at a time 
    app.topPad = 20
    resetRecentPage(app)

    # initialize block chain viewing page details
    app.blockWidth = 3
    app.currBlocks = app.blocks[0:app.blockWidth]
    app.blockIndex = 0
    resetViewPage(app)
    # initIndex(app)
    # populate(app, 1000)

def resetViewPage(app):
    app.index = 0
    app.viewingBlockTxs = False
    maxChainTxsViewable = min(app.txWidth, len(app.myTxs))
    app.currTxs = app.myTxs[0:maxChainTxsViewable] # currently viewable transactions

def resetRecentPage(app):
    app.index = 0
    app.myTxs = testMyTxs2() # all of user's transactions
    maxRecentViewable = min(app.txWidth, len(app.myTxs))
    app.currTxs = app.myTxs[0:maxRecentViewable] # currently viewable transactions

def timerFired(app):
    app.timerDelay = 250

def pageHandler(app, event):
    if event.key == "Right":
        app.page += 1
        if app.page > 5:
            app.page = 0
        return True
    if event.key == "Left":
        app.page -= 1
        if app.page < 0:
            app.page = 5
        return True

def keyPressed(app, event):
    if pageHandler(app, event):
        return
    elif app.page == 0:
        tutorialKeyHandler(app, event)
    elif app.page == 1:
        overviewKeyHandler(app, event)
    elif app.page == 2:
        sendKeyHandler(app, event)
    elif app.page == 3:
        mintKeyHandler(app, event)
    elif app.page == 4:
        recentKeyHandler(app, event)
    elif app.page == 5:
        viewKeyHandler(app, event)

def mousePressed(app, event):
    navBarClickHandler(app, event)
    if app.page == 0:
        tutorialClickHandler(app, event)
    elif app.page == 1:
        overviewClickHandler(app, event)
    elif app.page == 2:
        sendClickHandler(app, event)
    elif app.page == 3:
        mintClickHandler(app, event)
    elif app.page == 4:
        recentClickHandler(app, event)
    elif app.page == 5:
        viewClickHandler(app, event)

def redrawAll(app, canvas):
    drawNavbar(app, canvas)
    if app.page == 0:
        drawTutorial(app, canvas)
    elif app.page == 1:
        drawOverview(app, canvas)
    elif app.page == 2:
        drawSend(app, canvas)
    elif app.page == 3:
        drawMint(app, canvas)
    elif app.page == 4:
        drawRecent(app, canvas)
    elif app.page == 5:
        drawView(app, canvas)

# makeInitialTable()
runApp(width=700, height=500)