import math

def tutorialKeyHandler(app, event):
    pass

def overviewKeyHandler(app, event):
    if event.key == 's':
        try:
            stake = round(float(app.getUserInput("Enter stake amount: ")), 2)
            return app.chain.addStake(app.userAddress, stake)
        except Exception as error:
            print(error)

def sendKeyHandler(app, event):
    pass

def mintKeyHandler(app, event):
    if event.key == 'Down':
        moveIndex(app, 1)
    elif event.key == 'Up':
        moveIndex(app, -1)
    elif event.key == "s":
        moveIndex(app, -app.index)

def recentKeyHandler(app, event):
    if event.key == 'Down':
        moveIndex(app, 1)
    elif event.key == 'Up':
        moveIndex(app, -1)
    elif event.key == "s":
        moveIndex(app, -app.index)

# moves the start tx index in the list of txs shown
def moveIndex(app, Dir):
    if app.page == 1 or app.page == 2: # don't worry about moving on these pages
        return
    if app.page == 3: # mint page
        txsCount = len(app.txsPool)
        maxViewable = min(txsCount, app.txsPoolWidth)
        txWidth = app.txsPoolWidth
    elif app.page == 4: # recent page
        txsCount = len(app.humanUserTxs[app.userAddress])
        maxViewable = min(app.txWidth, txsCount)
        txWidth = app.txWidth
    elif app.page == 5: # block viewing page
        currBlockTxs = app.currBlocks[app.blockTxsIndex].txs
        txsCount = len(currBlockTxs)
        maxViewable = min(app.txWidth, txsCount)
        txWidth = app.txWidth
    app.index += Dir
    if txWidth > maxViewable:
        app.index += Dir
    if app.index < 0:
        app.index = 0
    elif app.index > txsCount - txWidth:
        app.index = txsCount - txWidth

    # refresh our stored current txs, we can call moveIndex(app, 0) to do this function without moving index
    if app.page == 3:
        app.currPoolTxs = app.txsPool[app.index: app.index + app.txsPoolWidth]
    elif app.page == 4:
        app.currRecentTxs = app.humanUserTxs[app.userAddress][app.index: app.index + app.txWidth]
    elif app.page == 5:
        app.currBlockTxs = currBlockTxs[app.index: app.index + app.txWidth]

# TODO fix list index out of range bug when < 3 blocks exist in chain 
def viewKeyHandler(app, event): 
    if event.key == '0':
        app.viewingBlockTxs = False
    elif event.key == '1':
        app.viewingBlockTxs = True
        app.blockTxsIndex = 0
        moveIndex(app, 0)
    elif event.key == '2':
        if len(app.chain.blocks) < 2:
            return
        app.viewingBlockTxs = True
        app.blockTxsIndex = 1
        moveIndex(app, 0)
    elif event.key == "3":
        if len(app.chain.blocks) < 3:
            return
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
        app.blockIndex = 0 # we dont have enough blocks to fill screen, so dont move index
    elif app.blockIndex < 0:
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
    # button clicks 
    B1X0, B1Y0, B1X1, B1Y1, text1 = app.sendButton1
    B2X0, B2Y0, B2X1, B2Y1, text2 = app.sendButton2
    B3X0, B3Y0, B3X1, B3Y1, text3 = app.sendButton3
    inButton1 = (B1X0 <= event.x <= B1X1) and (B1Y0 <= event.y <= B1Y1)
    inButton2 = (B2X0 <= event.x <= B2X1) and (B2Y0 <= event.y <= B2Y1)
    inButton3 = (B3X0 <= event.x <= B3X1) and (B3Y0 <= event.y <= B3Y1)
    if inButton1:
        app.recAddress = app.getUserInput("Receiver Address:")
    elif inButton2:
        app.sendAmount = app.getUserInput("Enter an amount:")
    elif inButton3:
        receiver = app.recAddress
        try:
            amt = round(float(app.sendAmount), 2)
            app.txsPool.append(app.currUser.send(receiver, amt))
            app.showMessage('Send Message', 'Transaction Sent to Pool!')
            
            # refresh our mint page if we are on it
            app.index = 0
            maxPoolViewable = min(app.txsPoolWidth, len(app.txsPool))
            app.currPoolTxs = app.txsPool[0:maxPoolViewable]
        except Exception as error:
            print(error)
            app.showMessage('Send Error', 'Please enter a number!')

def mintClickHandler(app, event):
    txTableClickHandler(app, event)

def recentClickHandler(app, event):
    txTableClickHandler(app, event)

def txTableClickHandler(app, event):
    if app.page == 3:
        topPad = 60 # extra space given on mintPage
        txWidth = app.txsPoolWidth
        txStart = app.topMargin + app.topPad + topPad
        txBoxHeight = (app.height - (2*app.topMargin + topPad))//txWidth
        txEnd = app.height-app.topMargin
    else:
        txWidth = app.txWidth
        txBoxHeight = (app.height - 2*app.topMargin)//txWidth
        txStart = app.topMargin + app.topPad
        txEnd = app.height-app.topMargin

    # we are inside a transaction box
    if (event.y > txStart) and (event.y < txStart + app.txWidth*txBoxHeight):
        box = math.floor((event.y - txStart)/txBoxHeight)
        # select correct currTxs List
        if app.page == 3:
            txs = app.currPoolTxs
        if app.page == 4:
            txs = app.currRecentTxs
        elif app.page == 5:
            txs = app.currBlockTxs
        
        # ignore case when box # is more than len(txs)
        if box >= len(txs):
            return

        # check if it's already selected, if so then load popup
        if app.currTxBox == box:
            tx = txs[box]
            msg = f'{tx.senderKey[0:15]}... to {tx.receiver[0:15]}...\n{box}\nyay'
            app.showMessage('Transaction', msg)
        app.currTxBox = box
    else:
        app.currTxBox = -1 # if its -1 we don't highlight any of the boxes


    

def viewClickHandler(app, event):
    # load individual messageBox popup for specific tx clicked
    if app.viewingBlockTxs:
        txTableClickHandler(app, event)
    elif event.y > app.topMargin:
        if event.x < app.sideMargin*3:
            moveBlockIndex(app, -1)
        elif event.x > app.width - 3*app.sideMargin:
            moveBlockIndex(app, +1)

def sendMouseHandler(app, event):
    B1X0, B1Y0, B1X1, B1Y1, text1 = app.sendButton1
    B2X0, B2Y0, B2X1, B2Y1, text2 = app.sendButton2
    B3X0, B3Y0, B3X1, B3Y1, text3 = app.sendButton3
    inButton1 = (B1X0 <= event.x <= B1X1) and (B1Y0 <= event.y <= B1Y1)
    inButton2 = (B2X0 <= event.x <= B2X1) and (B2Y0 <= event.y <= B2Y1)
    inButton3 = (B3X0 <= event.x <= B3X1) and (B3Y0 <= event.y <= B3Y1)
    if app.sendButton1Color == 'white' and inButton1:
        app.sendButton1Color = 'lightGrey'
    elif app.sendButton1Color == 'lightGrey' and not inButton1:
        app.sendButton1Color = 'white'
    
    elif app.sendButton2Color == 'white' and inButton2:
        app.sendButton2Color = 'lightGrey'
    elif app.sendButton2Color == 'lightGrey' and not inButton2:
        app.sendButton2Color = 'white'

    elif app.sendButton3Color == 'white' and inButton3:
        app.sendButton3Color = 'lightGrey'
    elif app.sendButton3Color == 'lightGrey' and not inButton3:
        app.sendButton3Color = 'white'