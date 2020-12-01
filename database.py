
import sqlite3, json
'''
-------------------SQL DATABASE REFERENCES---------------
chain.db - stores table of blocks, users, and main User

TABLES:
    chain.db:
        blocks: JSON rawstring of blocks, column id - 1 is the block height
        users: JSON rawstring of user objects, keys in hex represntation
        User: JSON rawstring of main User
'''

#######################################################
#                  LOADING FUNCTIONS
#######################################################

# fetches the user data from humanusers table, multiple keypairs possible
def fetchHumanUsers():
    query = "SELECT * From humanusers"
    return sqlTransaction(query, fetch=True)

# fetches the computer users data from the compusers table
def fetchCompUsers():
    query = "SELECT * From compusers"
    return sqlTransaction(query, fetch=True)

#returns list of n random transactions
def makeTxs(n):
    txs = []
    for tx in range(n):
        txs.append(createTx())
    return txs

#try, except, finally format taken from https://pynative.com/python-sqlite/ 
def makeTable(name, blocks=True):
    try:
        database = sqlite3.connect('chain.db')
        #initialize our cursor object, which allows us to interact with our created database
        c = database.cursor()
        if blocks: # we require an extra ID column for an easy to access block height
            query = '''CREATE TABLE %s (
                            id integer primary key autoincrement,
                            block text
                            )''' %name
        else: # just make one text column for the json rawstring
            query = '''CREATE TABLE %s (
                            user text
                            )''' %name
        c.execute(query)
        print(f"Table {name} Created in chain.db!")
    except sqlite3.Error as error:
        print("Sqlite error returned: ", error)
    finally:
        if database:
            database.close()

def delTable(table, dbname):
    try:
        database = sqlite3.connect(dbname)
        c = database.cursor()
        query = f'DROP TABLE {table}'
        c.execute(query)
        database.commit()
    except sqlite3.Error as error:
        print("Sqlite error returned: ", error)
    finally:
        if database:
            database.close()
            print("The %s table was Dropped!"%table)

def sqlTransaction(query, msg='', fetch=False):
    try:
        database = sqlite3.connect('chain.db')
        #initialize our cursor object, which allows us to interact with our created database
        c = database.cursor()
        c.execute(query)
        result = c.fetchall()
        database.commit()
        print(msg)
    except sqlite3.Error as error:
        print("Sqlite error returned: ", error)
    finally:
        if database:
            database.close()
        if fetch:
            return result 

#######################################################
#                  INSERT FUNCTIONS
#######################################################


''' CURRENTY UNNECESSARY
# returns dictionary representation of the block at specified height
def blockDeserializer(height):
    # we fetch our id from the height+1 because of starting at 1 in the db
    query = "SELECT * FROM blocks WHERE id = %s" %(height+1)
    rawString = sqlTransaction(query, fetch=True)[0][1]
    d = json.loads(rawString)
    return d
'''

def insertBlock(block):
    msg = "Inserted Block into chain.db!"
    query = "INSERT INTO blocks (block) VALUES ('%s')" %block.rawString
    sqlTransaction(query, msg)

def insertHumanUser(user):
    msg = "Inserted User into chain.db"
    query = "INSERT INTO humanusers (user) VALUES ('%s')" %user.rawString
    sqlTransaction(query, msg)