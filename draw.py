import time

def drawNavbar(app, canvas):
    boxWidth = (app.width)/len(app.pages)
    boxHeight = app.topMargin
    for i in range(len(app.pages)):
        name = app.pages[i]
        color = 'white'
        if app.page == i:
            color = 'lightGrey'
        x0, y0 = i*boxWidth, 0
        x1, y1 = x0+boxWidth, boxHeight
        mid = (x0+x1)/2
        canvas.create_rectangle(x0, y0, x1, y1, fill=color, width=1)
        canvas.create_text(mid, boxHeight/2, text=name, font='Arial 10 bold')
        
def drawTutorial(app, canvas):
    # canvas.create_text()
    pass

def drawOverview(app, canvas):
    pass

def drawSend(app, canvas):
    pass

def drawMint(app, canvas):
    pass

def drawRecent(app, canvas):
    colsX = drawTxColumns(app, canvas)
    viewableTxs = min(app.txWidth, len(app.myTxs))
    drawTxs(app, canvas, colsX, viewableTxs, app.currTxs)

def drawTxColumns(app, canvas):
    topPad = 20
    tableWidth = app.width-2*app.sideMargin
    startY, endY = app.topMargin, app.topMargin + topPad

    # Date Column
    dateWidth = 2*tableWidth/7
    dateEnd = app.sideMargin + dateWidth
    canvas.create_rectangle(app.sideMargin, startY, dateEnd, endY)
    canvas.create_text((app.sideMargin+dateWidth)/2, app.topMargin + topPad/2, text='Date', font="Arial 14 bold")

    # Type Column
    typeWidth = tableWidth/7
    typeEnd = app.sideMargin + dateWidth + typeWidth
    canvas.create_rectangle(dateEnd, startY, typeEnd, endY)
    canvas.create_text((dateEnd+typeEnd)/2, app.topMargin + topPad/2, text='Type', font="Arial 14 bold")

    # Label Column
    labelWidth = 3*tableWidth/7
    labelEnd = typeEnd + labelWidth
    canvas.create_rectangle(typeEnd, startY, labelEnd, endY)
    canvas.create_text((typeEnd+labelEnd)/2, app.topMargin + topPad/2, text='Label', font="Arial 14 bold")

    # Amount Column
    amtWidth = tableWidth/7
    amtEnd = labelEnd + amtWidth
    canvas.create_rectangle(labelEnd, startY, amtEnd, endY)
    canvas.create_text((labelEnd+amtEnd)/2, app.topMargin + topPad/2, text='Amount', font="Arial 14 bold")

    colsX = app.sideMargin, dateEnd, typeEnd, labelEnd
    canvas.create_text(app.width/2, app.height-app.topMargin/2, text="Up/Down to move, s to go to start")
    return colsX

def drawTxs(app, canvas, colsX, viewable, txs):
    txBoxHeight = (app.height - 2*app.topMargin)//app.txWidth
    if app.index%2 == 0:
        colorMode = 0
    else:
        colorMode = 1
    for i in range(viewable):
        if colorMode == 1:
            if i%2 == 0:
                color = 'lightGrey'
            else:
                color = 'white'
        else:
            if i%2 == 0:
                color = 'white'
            else:
                color = 'lightGrey'

        tx = txs[i]
        x0, y0 = app.sideMargin, app.topMargin + app.topPad + i*txBoxHeight
        drawTx(app, canvas, tx, x0, y0, colsX, color)

def drawTx(app, canvas, tx, x0, y0, colsX, color):
    txBoxHeight = (app.height - 2*app.topMargin)//app.txWidth 
    txBoxWidth = app.width - 2*app.sideMargin
    canvas.create_rectangle(x0, y0, x0 + txBoxWidth, y0 + txBoxHeight, width=2, fill=color)
    txtCy = y0 + txBoxHeight/2
    sender, receiver, amt, date = tx.sender, tx.receiver, tx.amt, tx.date
    date = time.asctime(time.localtime(date))
    # label gives the useful address in the transaction because yours is already a given
    label, txType = 'N/A', 'N/A'
    if sender == "coinbase":
        txType = 'Minted'
        label = receiver
    elif sender == app.userAddress:
        txType = 'Sent To'
        label = receiver
    elif receiver == app.userAddress:
        txType = 'Received'
        label = sender

    pad = 10
    dateX, typeX, labelX, amtX = colsX
    # date column
    canvas.create_text(dateX+pad, txtCy, text=(f'{date}'), 
            font='Arial 8 bold', anchor='w')
    
    # type column
    canvas.create_text(typeX+pad, txtCy, text=(f'{txType}'), 
            font='Arial 8 bold', anchor='w')

    # label column
    canvas.create_text(labelX+pad, txtCy, text=(f'{label[0:15]}'), 
            font='Arial 8 bold', anchor='w')

    # amount column
    canvas.create_text(amtX+pad, txtCy, text=(f'{amt} (112C)'), 
            font='Arial 8 bold', anchor='w')

def drawView(app, canvas):
    
    # when user presses one of three keys (1,2,3) the transactions for that block are shown in a new draw page
    drawBlocks(app, canvas)
    if app.viewingBlockTxs:
        drawTxColumns(app, canvas)
        drawBlockTxs(app, canvas, app.currBlocks[app.viewBlockIndex])

def drawBlocks(app, canvas):
    block1, block2, block3 = None, None, None
    if len(app.blocks) == 1:
        block1 = app.blocks[0]
    elif len(app.blocks) == 2:
        block1, block2 = app.blocks[0], app.blocks[1]
    elif len(app.blocks) == 3:
        block1, block2, block3 = app.blocks[0], app.blocks[1], app.blocks[2]
    else:
        block1, block2, block3 = app.currBlocks[0], app.currBlocks[1], app.currBlocks[2]

    # first block
    canvas.create_text(app.width/4, app.height/4, text=str(block1))

    # second block
    canvas.create_text(app.width/2, app.height/3, text=str(block2))

    # third block
    canvas.create_text(3*app.width/4, app.height/2, text=str(block3))



def drawBlockTxs(app, canvas, block):
    viewableTxs = min(app.txWidth, len(block.txs))
    drawTxs(app, canvas, viewableTxs, block.txs)

