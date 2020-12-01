import time

# takes time in seconds since epoch and returns short version string MM/DD/YY-HH:MM:SS
def formatTime(Time):
    struct = time.localtime(Time)
    return time.strftime("%m/%d/%y--%H:%M:%S", struct)

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
    colsX = drawMyTxColumns(app, canvas)
    viewableTxs = min(app.txWidth, len(app.humanUserTxs[app.userAddress]))
    drawMyTxs(app, canvas, colsX, viewableTxs, app.currTxs)

def drawMyTxColumns(app, canvas):
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

def drawMyTxs(app, canvas, colsX, viewable, txs):
    txBoxHeight = (app.height - 2*app.topMargin)//app.txWidth
    if app.index%2 == 0:
        colorMode = 0
    else:
        colorMode = 1
    for i in range(viewable):
        # makes color unchangable when there are less than 10 txs, removing weird changing color effect
        if len(app.currTxs) < app.txWidth:
            colorMode = 0
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
        drawMyTx(app, canvas, tx, x0, y0, colsX, color)

def drawMyTx(app, canvas, tx, x0, y0, colsX, color):
    txBoxHeight = (app.height - 2*app.topMargin)//app.txWidth 
    txBoxWidth = app.width - 2*app.sideMargin
    canvas.create_rectangle(x0, y0, x0 + txBoxWidth, y0 + txBoxHeight, width=2, fill=color)
    txtCy = y0 + txBoxHeight/2
    sender, receiver, amt, date = tx.senderKey, tx.receiver, tx.amt, tx.date
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
    if app.viewingBlockTxs:
        maxViewable = len(app.currTxs)
        colsX = drawTxColumns(app, canvas)
        drawTxs(app, canvas, colsX, maxViewable, app.currTxs)
    else:
        drawBlocks(app, canvas)

def drawBlocks(app, canvas):
    i = 1
    for block in app.currBlocks:
        if i > 3:
            break
        drawBlock(app, canvas, block, i*app.sideMargin + (i-1)*app.blockDrawSize)
        i += 1

def drawBlock(app, canvas, block, x0):
    yPad = app.height/5
    blockBoxHeight = app.height - (app.topMargin + 2*yPad)
    x1 = x0+app.blockDrawSize
    y0 = app.topMargin + yPad
    y1 = y0 + blockBoxHeight
    canvas.create_rectangle(x0, y0, x1, y1, width=3)
    height = app.chain.blocks.index(block)

    heightY, timeY, minterY = 30, 5, 50
    prevHashY, hashY = y1 - 40, y1 - 70
    heightX = timeX = app.blockDrawSize/2
    minterX = prevHashX = hashX = 5
    canvas.create_text(x0 + heightX, y0 + heightY, text=f'Block: {height}', font='Arial 12 bold')
    canvas.create_text(x0 + timeX, y0 + timeY, text=formatTime(block.time), anchor='n', font='Arial 8')
    canvas.create_text(x0 + minterX, y0 + minterY, text=f'Minter: {block.minter}', anchor='nw', font='Arial 10 bold')

    prevText = str(block.prevHash)[0:30] + '...'
    if block.prevHash == '0':
        prevText = 'None'
    canvas.create_text(x0 + prevHashX, prevHashY, text="Pevious Block's Hash:", anchor='nw', font='Arial 10 bold')
    canvas.create_text(x0 + prevHashX, prevHashY + 15, text=prevText, anchor='nw', font='Arial 8')

    hashText = f'{block.hash[0:30]}...'
    canvas.create_text(x0 + hashX, hashY, text="This Block's Hash: ", anchor='nw', font='Arial 10 bold')
    canvas.create_text(x0 + hashX, hashY + 15, text=hashText, anchor='nw', font='Arial 8')
    yStart, yEnd = y0 + minterY + 15, y1 - 85
    drawBriefTxs(app, canvas, block.txs[0:3], x0, yStart, x1, yEnd)

def drawBriefTxs(app, canvas, txs, x0, y0, x1, y1):
    if txs == []:
        canvas.create_text((x0+x1)/2, (y0+y1)/2, text='No Transactions!', font='Arial 18 bold')
    txBoxHeight = (y1-y0)/3
    for i in range(len(txs)):
        yStart = y0 + i*txBoxHeight
        yEnd = yStart + txBoxHeight
        txtCy = (yStart + yEnd)/2

        canvas.create_rectangle(x0, yStart, x1, yEnd, width=2)
        tx = txs[i]
        tableWidth = (x1-x0)
        
        # sender column
        sendWidth = 3*tableWidth/7
        sendEnd = x0 + 10 + sendWidth
        senderTxt = str(tx.senderKey)[0:15] + '... -->'
        canvas.create_text(x0 + 10, txtCy, text=senderTxt, 
                font='Arial 8', anchor='w')

        # receiver column
        recWidth = 3*tableWidth/7
        recEnd = sendEnd + recWidth
        receiverTxt = str(tx.receiver)[0:15] + '...'
        canvas.create_text(sendEnd, txtCy, text=receiverTxt, 
                font='Arial 8', anchor='w')

        # amount column
        amtWidth = tableWidth/7
        canvas.create_text(recEnd, txtCy, text=tx.amt, font='Arial 8 bold', anchor='w')

def drawTxColumns(app, canvas):
    topPad = 20
    tableWidth = app.width-2*app.sideMargin
    startY, endY = app.topMargin, app.topMargin + topPad

    # Date Column
    dateWidth = 2*tableWidth/11
    dateEnd = app.sideMargin + dateWidth
    canvas.create_rectangle(app.sideMargin, startY, dateEnd, endY)
    canvas.create_text((app.sideMargin+dateWidth)/2, app.topMargin + topPad/2, text='Date', font="Arial 14 bold")

    # Sender Column
    sendWidth = 4*tableWidth/11
    sendEnd = app.sideMargin + dateWidth + sendWidth
    canvas.create_rectangle(dateEnd, startY, sendEnd, endY)
    canvas.create_text((dateEnd+sendEnd)/2, app.topMargin + topPad/2, text='Sender', font="Arial 14 bold")

    # Receiver Column
    recWidth = 4*tableWidth/11
    recEnd = sendEnd + recWidth
    canvas.create_rectangle(sendEnd, startY, recEnd, endY)
    canvas.create_text((sendEnd+recEnd)/2, app.topMargin + topPad/2, text='Label', font="Arial 14 bold")

    # Amount Column
    amtWidth = tableWidth/11
    amtEnd = recEnd + amtWidth
    canvas.create_rectangle(recEnd, startY, amtEnd, endY)
    canvas.create_text((recEnd+amtEnd)/2, app.topMargin + topPad/2, text='Amt', font="Arial 14 bold")

    colsX = app.sideMargin, dateEnd, sendEnd, recEnd
    canvas.create_text(app.width/2, app.height-app.topMargin/2, text="Up/Down to move, s to go to start")
    return colsX


# txs viewer draw function for a block's transactions
def drawTxs(app, canvas, colsX, viewable, txs):
    txBoxHeight = (app.height - 2*app.topMargin)//app.txWidth
    if app.index%2 == 0:
        colorMode = 0
    else:
        colorMode = 1
    for i in range(viewable):
        # makes color unchangable when there are less than 10 txs, removing weird changing color effect
        if len(app.currTxs) < app.txWidth:
            colorMode = 0
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
    sender, receiver, amt, date = str(tx.senderKey), str(tx.receiver), str(tx.amt), tx.date
    date = formatTime(date)
    pad = 10
    dateX, typeX, labelX, amtX = colsX
    
    # date column
    canvas.create_text(dateX+pad, txtCy, text=(f'{date}'), 
            font='Arial 8 bold', anchor='w')
    
    # sender column
    canvas.create_text(typeX+pad, txtCy, text=sender[0:20], 
            font='Arial 8 bold', anchor='w')

    # receiver column
    canvas.create_text(labelX+pad, txtCy, text=receiver[0:20], 
            font='Arial 8 bold', anchor='w')

    # amount column
    canvas.create_text(amtX, txtCy, text=(amt + '(112C)'), 
            font='Arial 8 bold', anchor='w')