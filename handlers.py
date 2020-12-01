import math

def tutorialKeyHandler(app, event):
    pass

def overviewKeyHandler(app, event):
    pass

def sendKeyHandler(app, event):
    pass

def mintKeyHandler(app, event):
    pass

def recentKeyHandler(app, event):
    if event.key == 'Down':
        moveIndex(app, 1)
    elif event.key == 'Up':
        moveIndex(app, -1)
    elif event.key == "s":
        moveIndex(app, -app.index)

# moves the start tx index in the list of txs shown
def moveIndex(app, Dir):
    if app.page == 4:
        txsCount = len(app.humanUserTxs[app.userAddress])
        maxViewable = min(app.txWidth, txsCount)
    elif app.page == 5:
        currBlockTxs = app.currBlocks[app.blockTxsIndex].txs
        txsCount = len(currBlockTxs)
        maxViewable = min(app.txWidth, txsCount)
    app.index += Dir
    if app.txWidth > maxViewable:
        app.index += Dir
    if app.index < 0:
        app.index = 0
    elif app.index > txsCount - app.txWidth:
        app.index = txsCount - app.txWidth
    if app.page == 4:
        app.currTxs = app.humanUserTxs[app.userAddress][app.index: app.index + app.txWidth]
    elif app.page == 5:
        app.currTxs = currBlockTxs[app.index: app.index + app.txWidth]

# TODO fix list index out of range bug when < 3 blocks exist in chain 
def viewKeyHandler(app, event): 
    if event.key == '0':
        app.viewingBlockTxs = False
    elif event.key == '1':
        app.viewingBlockTxs = True
        app.blockTxsIndex = 0
        moveIndex(app, 0)
    elif event.key == '2':
        app.viewingBlockTxs = True
        app.blockTxsIndex = 1
        moveIndex(app, 0)
    elif event.key == "3":
        app.viewingBlockTxs = True
        app.blockTxsIndex = 2
        moveIndex(app, 0)
    if app.viewingBlockTxs:
        viewBlockTxsKeyHandler(app, event)

def viewBlockTxsKeyHandler(app, event):
    if event.key == 'Down':
        moveIndex(app, 1)
    elif event.key == 'Up':
        moveIndex(app, -1)
    elif event.key == "s":
        moveIndex(app, -app.index)

def moveBlockIndex(app, Dir):
    blockCount = len(app.chain.blocks)
    maxViewable = min(app.blockWidth, blockCount)
    app.blockIndex += Dir
    if app.blockWidth > maxViewable:
        app.blockIndex += Dir
    if app.blockIndex < 0:
        app.blockIndex = 0
    elif app.blockIndex > blockCount - app.blockWidth:
        app.blockIndex = blockCount - app.blockWidth
    app.currBlocks = app.chain.blocks[app.blockIndex: app.blockIndex + app.blockWidth]

def navBarClickHandler(app, event):
    if event.y > app.topMargin:
        return
    boxWidth = app.width/len(app.pages)
    pageClicked = math.floor(event.x/boxWidth)
    app.page = pageClicked

def tutorialClickHandler(app, event):
    pass

def overviewClickHandler(app, event):
    pass

def sendClickHandler(app, event):
    pass

def mintClickHandler(app, event):
    pass

def recentClickHandler(app, event):
    txTableClickHandler(app, event)

def txTableClickHandler(app, event):
    txBoxHeight = (app.height - 2*app.topMargin)//app.txWidth
    txStart = app.topMargin + app.topPad
    txEnd = app.height-app.topMargin
    if (event.y > txStart) and (event.y < txStart + app.txWidth*txBoxHeight):
        box = math.floor((event.y - txStart)/txBoxHeight)

def viewClickHandler(app, event):
    if event.y > app.topMargin:
        if event.x < app.sideMargin*3:
            moveBlockIndex(app, -1)
        elif event.x > app.width - 3*app.sideMargin:
            moveBlockIndex(app, +1)